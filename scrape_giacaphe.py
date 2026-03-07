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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

URL_SCRAPE = "https://giacaphe.com/gia-ca-phe-noi-dia/"

# PHP API Configuration
PHP_ENDPOINT = os.environ.get("PHP_ENDPOINT", "https://agriht.com/gianongsan1.php")
SECRET_KEY   = os.environ.get("SECRET_KEY", "ditmecuocdoi")

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

def send_onesignal_notification(records: list[dict]):
    """Gửi thông báo OneSignal với giá nông sản"""
    if not ONESIGNAL_APP_ID or not ONESIGNAL_REST_API_KEY:
        log.warning("⚠️  OneSignal không được cấu hình, bỏ qua thông báo")
        return
    
    if not records:
        return
    
    # Format message với top 5 sản phẩm có thay đổi
    sorted_records = sorted(records, key=lambda x: abs(x.get('thay_doi', 0)), reverse=True)
    top_records = sorted_records[:5]
    
    message_lines = ["Giá nông sản hôm nay có sự biến động như sau:"]
    for rec in top_records:
        thi_truong = rec['thi_truong']
        gia = rec['gia_trung_binh']
        thay_doi = rec['thay_doi']
        # Format: Đắk Lắk 96,000 +1,200 (dùng dấu phẩy như user yêu cầu)
        gia_str = f"{int(gia):,}"
        thay_doi_str = f"{int(thay_doi):+,}" if thay_doi != 0 else "--"
        message_lines.append(f"{thi_truong} {gia_str} {thay_doi_str}")
    
    message = "\n".join(message_lines)
    
    # Payload OneSignal
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "included_segments": ["All"],  # Gửi cho tất cả người dùng đã subscribe
        "headings": {"en": "Giá Nông Sản Mới"},
        "contents": {"en": message},
        "url": "https://agriht.com/gia-nong-san/",
        "data": {
            "type": "price_update",
            "count": len(records)
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

def post_to_php(records: list[dict]):
    """POST dữ liệu tới PHP endpoint với SECRET_KEY"""
    if not records:
        log.warning("Không có dữ liệu để POST!")
        return
    
    log.info("📡 POST tới: %s", PHP_ENDPOINT)
    log.info("🔑 Secret Key: %s", SECRET_KEY[:5] + "***")
    
    try:
        response = requests.post(
            PHP_ENDPOINT,
            json=records,
            headers={
                "Content-Type": "application/json",
                "X-Secret-Key": SECRET_KEY
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            inserted = result.get("inserted", 0)
            updated = result.get("updated", 0)
            
            log.info("✅ Hoàn thành!")
            log.info("  - Inserted: %d", inserted)
            log.info("  - Updated: %d", updated)
            
            if result.get("errors"):
                log.warning("  - Errors: %s", result["errors"])
            
            # Gửi thông báo OneSignal sau khi cập nhật thành công
            send_onesignal_notification(records)
        elif response.status_code == 401:
            log.error("❌ Unauthorized - SECRET_KEY không đúng!")
            raise SystemExit(1)
        else:
            log.error("❌ HTTP Error %d: %s", response.status_code, response.text)
            raise SystemExit(1)
            
    except Exception as e:
        log.error("❌ Lỗi kết nối: %s", e)
        raise SystemExit(1)

if __name__ == "__main__":
    img = chup_bang_gia()
    records = ocr_bang_gia(img)
    post_to_php(records)