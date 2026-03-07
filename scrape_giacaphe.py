#!/usr/bin/env python3
"""
scrape_giacaphe.py
Playwright chụp ảnh bảng giá → Tesseract OCR đọc → POST vào DB
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import re
import logging
import requests
import unicodedata
from datetime import datetime, date
from playwright.sync_api import sync_playwright
from PIL import Image
import pytesseract
import io
from decimal import Decimal

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

URL_SCRAPE = "https://giacaphe.com/gia-ca-phe-noi-dia/"

# Database Connection Mode
USE_MYSQL_DIRECT = os.environ.get("USE_MYSQL_DIRECT", "true").lower() == "true"

# PHP API Configuration
PHP_ENDPOINT = os.environ.get("PHP_ENDPOINT", "https://agriht.com/gianongsan1.php")
SECRET_KEY   = os.environ.get("SECRET_KEY", "ditmecuocdoi")

# MySQL Configuration
DB_CONFIG = {
    "host":     os.environ.get("DB_HOST", "srv1631.hstgr.io"),
    "port":     int(os.environ.get("DB_PORT") or "3306"),
    "database": os.environ.get("DB_NAME", "u697673786_Agriht"),
    "user":     os.environ.get("DB_USER", "u697673786_Agriht"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "charset":  "utf8mb4",
    "connection_timeout": int(os.environ.get("DB_TIMEOUT") or "12"),
    "autocommit": True,
}

# OneSignal Configuration
ONESIGNAL_APP_ID = os.environ.get("ONESIGNAL_APP_ID", "")
ONESIGNAL_REST_API_KEY = os.environ.get("ONESIGNAL_REST_API_KEY", "")
ONESIGNAL_URL = "https://onesignal.com/api/v1/notifications"

def chup_bang_gia() -> bytes:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1200, "height": 900},
            device_scale_factor=2,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()
        log.info("Load trang...")
        page.goto(URL_SCRAPE, wait_until="domcontentloaded", timeout=60_000)
        page.wait_for_timeout(5000)

        # Ẩn quảng cáo/popup để giảm nhiễu OCR.
        page.add_style_tag(
            content=(
                "iframe, .adsbygoogle, [id*='ads'], [class*='ads'], "
                "[id*='banner'], [class*='banner'], .quangcao, .advertisement "
                "{ display: none !important; }"
            )
        )
        page.wait_for_timeout(1000)

        table = None
        for t in page.query_selector_all("table"):
            txt = (t.inner_text() or "").lower()
            if any(k in txt for k in ["đắk lắk", "dak lak", "lâm đồng", "lam dong", "hồ tiêu", "ho tieu"]):
                table = t
                break
        if table is None:
            table = page.query_selector("table")

        if table:
            table.scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            img_bytes = table.screenshot()
            log.info("Chụp bảng: %d bytes", len(img_bytes))
        else:
            img_bytes = page.screenshot()
            log.warning("Không thấy bảng, chụp toàn trang")

        with open("screenshot_table.png", "wb") as f:
            f.write(img_bytes)

        context.close()
        browser.close()
    return img_bytes

def parse_so(text: str) -> float:
    """Parse số từ string, bỏ dấu chấm/phẩy ngàn"""
    clean = re.sub(r"[^\d]", "", text)
    return float(clean) if clean else 0.0


def normalize_text(text: str) -> str:
    """Lowercase + remove accents for tolerant matching."""
    t = unicodedata.normalize("NFD", text.lower())
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    t = t.replace("đ", "d")
    return re.sub(r"\s+", " ", t).strip()


def canonical_market_name(name: str) -> str:
    """Map noisy OCR market names to canonical labels."""
    n = normalize_text(name)

    if "dak lak" in n:
        return "Đắk Lắk"
    if "lam dong" in n:
        return "Lâm Đồng"
    if "gia lai" in n:
        return "Gia Lai"
    if "dak nong" in n or "dak noi" in n:
        return "Đắk Nông"
    if "ho tieu" in n or "ho tie" in n:
        return "Hồ tiêu"
    if "ty gia" in n or "usd" in n:
        return "Tỷ giá USD/VND"

    return ""


def parse_lines_to_records(lines: list[str]) -> list[dict]:
    """Parse text lines (from HTML table or OCR) into structured records."""
    today = date.today().isoformat()
    now = datetime.now().strftime("%H:%M:%S")

    records = []
    ty_gia = 0.0

    for line in lines:
        # Loại các dòng nhiễu gần như không có ký tự chữ/số hợp lệ
        if len(re.sub(r"[^\w\dÀ-ỹ]", "", line)) < 3:
            continue

        # Chuẩn hoá các lỗi OCR phổ biến ở dấu phân cách ngàn
        normalized_line = line.replace("/", ",")
        normalized_line = re.sub(r"\s+", " ", normalized_line).strip()

        # Tìm token số kiểu 96,000 hoặc +1,200 (chấp nhận OCR bị thiếu 1 chữ số)
        tokens = re.findall(r"[+\-]?\d{1,3}[.,]\d{2,3}", normalized_line)
        if not tokens:
            continue

        raw_market = re.split(r"[+\-]?\d", normalized_line)[0].strip()
        raw_market = re.sub(r"\s+", " ", raw_market)
        thi_truong = canonical_market_name(raw_market)
        if not thi_truong:
            continue

        lower_market = thi_truong.lower()

        # Header/footer
        if any(w in lower_market for w in ["thị trường", "trung bình", "theo:", "nguồn", "thay đổi"]):
            continue

        # Tỷ giá USD/VND
        if "tỷ giá" in lower_market or "ty gia" in lower_market or "usd" in lower_market:
            try:
                ty_gia = parse_so(tokens[0])
            except Exception:
                pass
            continue

        try:
            gia = parse_so(tokens[0])
        except Exception:
            continue

        if gia < 10_000:
            continue

        thay_doi = 0.0
        if len(tokens) > 1:
            try:
                sign = -1 if tokens[1].startswith("-") else 1
                thay_doi = parse_so(tokens[1]) * sign
            except Exception:
                pass

        san_pham = "Tiêu" if "tiêu" in lower_market else "Cà phê"

        records.append(
            {
                "ngay_cap_nhat": today,
                "san_pham": san_pham,
                "thi_truong": thi_truong,
                "gia_trung_binh": gia,
                "thay_doi": thay_doi,
                "ty_gia_usd_vnd": 0,
                "cap_nhat_luc": now,
            }
        )

    # Remove duplicate markets while keeping the first parsed row.
    unique = {}
    for rec in records:
        unique.setdefault(rec["thi_truong"], rec)
    records = list(unique.values())

    for r in records:
        r["ty_gia_usd_vnd"] = ty_gia
        log.info(
            "  >>> %s | %s | %.0f đ | %+.0f",
            r["san_pham"],
            r["thi_truong"],
            r["gia_trung_binh"],
            r["thay_doi"],
        )

    log.info("Tổng: %d bản ghi | Tỷ giá: %.0f", len(records), ty_gia)
    return records

def ocr_bang_gia(img_bytes: bytes) -> list[dict]:
    img = Image.open(io.BytesIO(img_bytes))
    w, h = img.size
    
    # Xử lý ảnh để OCR tốt hơn
    # 1. Convert sang grayscale
    img = img.convert('L')
    
    # 2. Resize về kích thước chuẩn nếu quá lớn (tránh OCR lỗi)
    if w > 1500:
        scale = 1500 / w
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        w, h = img.size
    
    # 3. Resize lên 2x để tăng độ nét cho chữ nhỏ
    img = img.resize((w * 2, h * 2), Image.LANCZOS)
    
    # 4. Denoise - làm mượt ảnh trước
    from PIL import ImageFilter, ImageEnhance, ImageOps
    img = img.filter(ImageFilter.MedianFilter(size=3))  # Loại bỏ noise
    
    # 5. Tăng sharpness để chữ rõ hơn
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2.0)
    
    # 6. Tăng contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.5)
    
    # 7. Binary threshold - chuyển thành đen/trắng rõ ràng
    img = img.point(lambda x: 0 if x < 130 else 255, '1')
    
    # Lưu ảnh processed để debug
    img.save("screenshot_processed.png")

    # Chạy nhiều lượt OCR để tăng tỉ lệ bắt đúng dòng dữ liệu.
    configs = [
        "--psm 6 --oem 3",
        "--psm 4 --oem 3",
        "--psm 11 --oem 3",
    ]

    all_lines = []
    for idx, cfg in enumerate(configs, start=1):
        text = pytesseract.image_to_string(img, lang="vie", config=cfg)
        if idx == 1:
            log.info("OCR output (pass %d):\n%s", idx, text)
        else:
            log.debug("OCR pass %d length: %d", idx, len(text))
        pass_lines = [l.strip() for l in text.splitlines() if l.strip()]
        all_lines.extend(pass_lines)

    # Nối cặp dòng liền nhau để xử lý trường hợp OCR tách market và giá thành 2 dòng.
    merged_lines = list(all_lines)
    for i in range(len(all_lines) - 1):
        merged_lines.append(f"{all_lines[i]} {all_lines[i + 1]}")

    return parse_lines_to_records(merged_lines)

def send_onesignal_notification(records: list[dict], inserted: int = 0, updated: int = 0):
    """Gửi thông báo OneSignal sau mỗi lần cập nhật thành công."""
    if not ONESIGNAL_APP_ID or not ONESIGNAL_REST_API_KEY:
        log.warning("⚠️  OneSignal không được cấu hình, bỏ qua thông báo")
        return
    
    if not records:
        return
    
    # Lọc các sản phẩm có biến động (thay_doi != 0)
    changed_records = [r for r in records if r.get('thay_doi', 0) != 0]

    today_label = datetime.now().strftime("%d/%m")

    # Có biến động: ưu tiên show các dòng thay đổi mạnh nhất.
    if not changed_records:
        log.info("ℹ️  Chưa có biến động giá lớn → Gửi bản tin giá trong ngày")
        display_records = sorted(records, key=lambda x: x['gia_trung_binh'], reverse=True)[:3]
        heading = f"Bản tin giá nông sản {today_label}"
        message_lines = ["Giá đã cập nhật, mời bạn xem nhanh:"]
    else:
        # Sort theo độ biến động giảm dần.
        display_records = sorted(changed_records, key=lambda x: abs(x.get('thay_doi', 0)), reverse=True)[:5]
        top = display_records[0]
        top_delta = int(top.get('thay_doi', 0))
        top_sign = "+" if top_delta > 0 else ""
        heading = f"Nóng: {top['thi_truong']} {top_sign}{top_delta:,}".replace(',', '.')
        message_lines = ["Giá vừa cập nhật, điểm qua thị trường nổi bật:"]

    message_lines.append(f"{inserted} mới | {updated} cập nhật")
    
    for rec in display_records:
        thi_truong = rec['thi_truong']
        gia = rec['gia_trung_binh']
        thay_doi = rec['thay_doi']
        # Format: Đắk Lắk 96,000 +1,200 (dùng dấu phẩy như user yêu cầu)
        gia_str = f"{int(gia):,}".replace(',', '.')  # 96.000 theo format VN
        if thay_doi != 0:
            thay_doi_str = f" ({int(thay_doi):+,})".replace(',', '.')
        else:
            thay_doi_str = ""
        message_lines.append(f"• {thi_truong}: {gia_str} đ{thay_doi_str}")
    
    message = "\n".join(message_lines)
    
    # Payload OneSignal
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "included_segments": ["All"],  # Gửi cho tất cả người dùng đã subscribe
        "headings": {"en": heading, "vi": heading},
        "contents": {"en": message, "vi": message},
        "url": "https://agriht.com/gia-nong-san/",
        "data": {
            "type": "price_update",
            "count": len(records),
            "inserted": inserted,
            "updated": updated,
        }
    }
    
    try:
        log.info("📢 Gửi thông báo OneSignal...")
        # OneSignal uses direct REST API Key with Basic prefix (no encoding needed)
        response = requests.post(
            ONESIGNAL_URL,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Basic {ONESIGNAL_REST_API_KEY}"
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            recipients = result.get("recipients", 0)
            log.info("✅ Đã gửi thông báo tới %d thiết bị", recipients)
        else:
            log.warning("⚠️  OneSignal error %d: %s", response.status_code, response.text[:200])
            
    except Exception as e:
        log.warning("⚠️  Lỗi gửi OneSignal: %s", e)

def post_to_mysql(records: list[dict]):
    """POST dữ liệu trực tiếp vào MySQL database (bypass CAPTCHA)"""
    if not records:
        log.warning("Không có dữ liệu để lưu!")
        return
    
    try:
        import mysql.connector
    except ImportError:
        log.error("❌ Cần cài đặt: pip install mysql-connector-python")
        raise SystemExit(1)
    
    log.info("📊 MySQL Direct Mode: %s", DB_CONFIG["host"])
    log.info("🔑 Database: %s", DB_CONFIG["database"])
    log.info("📤 Payload: %d records", len(records))
    
    try:
        log.info("Đang kết nối MySQL...")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        log.info("✅ Kết nối thành công!")
        
        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gia_nong_san (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                ngay_cap_nhat   DATE          NOT NULL,
                san_pham        VARCHAR(50)   NOT NULL,
                thi_truong      VARCHAR(100)  NOT NULL,
                gia_trung_binh  DECIMAL(15,2) DEFAULT 0,
                thay_doi        DECIMAL(10,2) DEFAULT 0,
                ty_gia_usd_vnd  DECIMAL(15,2) DEFAULT 0,
                cap_nhat_luc    TIME,
                UNIQUE KEY uq_ngay_sp_tt (ngay_cap_nhat, san_pham, thi_truong)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        sql = """
            INSERT INTO gia_nong_san
            (ngay_cap_nhat, san_pham, thi_truong, gia_trung_binh, thay_doi, ty_gia_usd_vnd, cap_nhat_luc)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            gia_trung_binh = VALUES(gia_trung_binh),
            thay_doi = VALUES(thay_doi),
            ty_gia_usd_vnd = VALUES(ty_gia_usd_vnd),
            cap_nhat_luc = VALUES(cap_nhat_luc)
        """
        
        inserted = 0
        updated = 0
        
        for record in records:
            cursor.execute(sql, (
                record['ngay_cap_nhat'],
                record['san_pham'],
                record['thi_truong'],
                Decimal(str(record['gia_trung_binh'])),
                Decimal(str(record['thay_doi'])),
                Decimal(str(record['ty_gia_usd_vnd'])),
                record['cap_nhat_luc']
            ))
            
            if cursor.rowcount == 1:
                inserted += 1
            elif cursor.rowcount == 2:
                updated += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        log.info("✅ Hoàn thành!")
        log.info("  - Inserted: %d", inserted)
        log.info("  - Updated: %d", updated)
        
        # Luôn gửi bản tin hằng ngày sau khi cập nhật thành công.
        log.info("📢 Gửi bản tin hằng ngày (inserted=%d, updated=%d)", inserted, updated)
        send_onesignal_notification(records, inserted=inserted, updated=updated)
            
    except mysql.connector.Error as e:
        log.error("❌ MySQL Error: %s", e)
        if e.errno == 2003:
            log.error("💡 Troubleshoot: Cần whitelist IP tại Hostinger → Remote MySQL")
        raise SystemExit(1)
    except Exception as e:
        log.error("❌ Lỗi: %s", e)
        raise SystemExit(1)

def post_to_php(records: list[dict]):
    """POST dữ liệu tới PHP endpoint với SECRET_KEY"""
    if not records:
        log.warning("Không có dữ liệu để POST!")
        return
    
    log.info("📡 POST tới: %s", PHP_ENDPOINT)
    log.info("🔑 Secret Key: %s", SECRET_KEY[:5] + "***")
    log.info("📤 Payload: %d records", len(records))
    
    # Debug: log payload đầu tiên
    if records:
        import json
        log.info("📤 Sample record: %s", json.dumps(records[0], ensure_ascii=False))
    
    try:
        response = requests.post(
            PHP_ENDPOINT,
            json=records,
            headers={
                "Content-Type": "application/json",
                "X-Secret-Key": SECRET_KEY,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://agriht.com/",
                "Origin": "https://agriht.com"
            },
            timeout=30
        )
        
        log.info("📥 Response status: %d", response.status_code)
        log.info("📥 Response content-type: %s", response.headers.get('Content-Type', 'unknown'))
        log.info("📥 Response text (first 500 chars): %s", response.text[:500])
        
        if response.status_code == 200:
            # Kiểm tra xem response có phải JSON không
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' not in content_type:
                log.error("❌ Response không phải JSON! Content-Type: %s", content_type)
                log.error("❌ Response body: %s", response.text[:1000])
                raise SystemExit(1)
            
            try:
                result = response.json()
            except ValueError as e:
                log.error("❌ Không thể parse JSON response: %s", e)
                log.error("❌ Response text: %s", response.text[:1000])
                raise SystemExit(1)
            
            inserted = result.get("inserted", 0)
            updated = result.get("updated", 0)
            
            log.info("✅ Hoàn thành!")
            log.info("  - Inserted: %d", inserted)
            log.info("  - Updated: %d", updated)
            
            if result.get("errors"):
                log.warning("  - Errors: %s", result["errors"])
            
            # Luôn gửi bản tin hằng ngày sau khi cập nhật thành công.
            log.info("📢 Gửi bản tin hằng ngày (inserted=%d, updated=%d)", inserted, updated)
            send_onesignal_notification(records, inserted=inserted, updated=updated)
        elif response.status_code == 401:
            log.error("❌ Unauthorized - SECRET_KEY không đúng!")
            raise SystemExit(1)
        else:
            log.error("❌ HTTP Error %d: %s", response.status_code, response.text)
            raise SystemExit(1)
            
    except Exception as e:
        log.error("❌ Lỗi kết nối: %s", e)
        raise SystemExit(1)

def post_records(records: list[dict]):
    """
    Wrapper function to post records using configured method:
    - MySQL direct (bypass CAPTCHA) if USE_MYSQL_DIRECT=true
    - PHP API endpoint if USE_MYSQL_DIRECT=false
    """
    if USE_MYSQL_DIRECT:
        log.info("🚀 Mode: MySQL Direct Connection (Bypass CAPTCHA)")
        post_to_mysql(records)
    else:
        log.info("🚀 Mode: PHP API Endpoint")
        post_to_php(records)

if __name__ == "__main__":
    img = chup_bang_gia()
    records = ocr_bang_gia(img)
    post_records(records)