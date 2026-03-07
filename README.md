# 🌾 Agri Scraper - Giá Nông Sản Tự Động

Scrape giá cà phê, tiêu từ **giacaphe.com** → **OCR parse** → **PHP API** → **MySQL database**

## 🎯 Kiến Trúc

- ✅ **GitHub Actions** → Chạy tự động mỗi 6 giờ
- ✅ **Playwright scraper** → Chụp bảng giá từ giacaphe.com
- ✅ **Tesseract OCR** → Đọc dữ liệu từ ảnh
- ✅ **PHP API** → Nhận dữ liệu với SECRET_KEY authentication
- ✅ **MySQL** → Lưu trữ dữ liệu giá nông sản

## 🚀 Quick Start

### 1. Setup (2 phút)

```bash
git clone <repo> && cd agri-scraper
python -m venv .venv
source .venv/bin/activate  # hoặc: .venv\Scripts\activate (Windows)
pip install -r requirements.txt
```

### 2. Cấu hình

Tạo file `.env`:

```bash
cp .env.example .env  # hoặc tạo file .env thủ công
```

```env
SECRET_KEY=ditmecuocdoi
PHP_ENDPOINT=https://agriht.com/gianongsan1.php
```

### 3. Test & Run

```bash
python test_post.py            # Test PHP endpoint
python test_onesignal.py       # Test OneSignal (optional, cần config trước)
python update_gianongsan.py    # Chạy scraper + POST + OneSignal
```

## ⚙️ GitHub Actions Setup

### 1. Add Secrets

Repository → **Settings** → **Secrets and variables** → **Actions**

Thêm secrets bắt buộc:
- `SECRET_KEY` = `ditmecuocdoi`
- `PHP_ENDPOINT` = `https://agriht.com/gianongsan1.php`

Thêm secrets tùy chọn (OneSignal Push Notification):
- `ONESIGNAL_APP_ID` = App ID của bạn từ OneSignal Dashboard
- `ONESIGNAL_REST_API_KEY` = REST API Key từ OneSignal

### 2. Trigger Workflow

**Actions** → **"Cập Nhật Giá Nông Sản"** → **Run workflow**

✅ Sẽ tự chạy mỗi 6 giờ (có thể thay đổi ở `.github/workflows/scrape.yml`)

## 📋 Biến Môi Trường

| Variable | Default | Note |
|----------|---------|------|
| `SECRET_KEY` | `ditmecuocdoi` | Secret key để xác thực PHP API |
| `PHP_ENDPOINT` | `https://agriht.com/gianongsan1.php` | URL của PHP endpoint |
| `ONESIGNAL_APP_ID` | (empty) | OneSignal App ID (tùy chọn) |
| `ONESIGNAL_REST_API_KEY` | (empty) | OneSignal REST API Key (tùy chọn) |

**Cách sử dụng:**
1. Tạo `.env` file (khuyến nghị)
2. Hoặc export biến: `export SECRET_KEY=ditmecuocdoi`

## � File Structure

| File | Purpose |
|------|---------|
| `scrape_giacaphe.py` | Main: Playwright screenshot + Tesseract OCR + POST to PHP + OneSignal |
| `update_gianongsan.py` | Wrapper script |
| `test_post.py` | Test PHP API endpoint |
| `test_onesignal.py` | Test OneSignal push notification |
| `gianongsan1.php` | PHP API nhận dữ liệu và insert vào MySQL |
| `ONESIGNAL_SETUP.md` | Hướng dẫn cấu hình OneSignal chi tiết |
| `.github/workflows/scrape.yml` | GitHub Actions (auto every 6h) |
| `requirements.txt` | Dependencies |
| `.env.example` | Environment template |

## 🐛 Troubleshooting

### ❌ "Unauthorized"

- Kiểm tra `SECRET_KEY` trong `.env` hoặc GitHub Secrets
- Đảm bảo SECRET_KEY khớp với giá trị trong `gianongsan1.php`

### ❌ "Connection timeout"

- Kiểm tra `PHP_ENDPOINT` URL đúng chưa
- Test thủ công: `curl -X POST -H "X-Secret-Key: ditmecuocdoi" https://agriht.com/gianongsan1.php`

### ⚠️ Setup PHP File

**Upload `gianongsan1.php` lên server của bạn:**
1. Mở Hostinger File Manager hoặc dùng FTP
2. Upload file `gianongsan1.php` vào thư mục `public_html/`
3. Đảm bảo file có quyền 644
4. Cập nhật MySQL credentials trong PHP file:
    ```php
    define('DB_PASS', 'YOUR_PASSWORD_HERE');
    ```

### 📢 OneSignal Push Notifications (Tùy chọn)

Xem hướng dẫn chi tiết: **[ONESIGNAL_SETUP.md](ONESIGNAL_SETUP.md)**

- ✅ Tự động gửi thông báo giá nông sản sau khi cập nhật thành công
- ✅ Hiển thị top 5 sản phẩm có biến động giá
- ✅ Tap vào thông báo → mở trang giá nông sản
- ⚠️ Nếu không cần OneSignal, bỏ qua (không ảnh hưởng scraper)


### ❌ "Table doesn't exist"

Script tự động tạo. Nếu error:

```bash
# Tạo thủ công ở Hostinger phpMyAdmin
CREATE TABLE gia_nong_san (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ngay_cap_nhat DATE NOT NULL,
    san_pham VARCHAR(50) NOT NULL,
    thi_truong VARCHAR(100) NOT NULL,
    gia_trung_binh DECIMAL(15,2) DEFAULT 0,
    thay_doi DECIMAL(10,2) DEFAULT 0,
    ty_gia_usd_vnd DECIMAL(15,2) DEFAULT 0,
    cap_nhat_luc TIME,
    UNIQUE KEY uq_ngay_sp_tt (ngay_cap_nhat, san_pham, thi_truong)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### ⚠️ OCR kết quả sai

- Cài Tesseract: `sudo apt-get install tesseract-ocr tesseract-ocr-vie`
- On Mac: `brew install tesseract`
- On Windows: https://github.com/UB-Mannheim/tesseract/wiki

## 📞 Support

- Check **Actions** tab for error logs
- Run locally: `python test_mysql.py` to debug
- Verify credentials in `.env` file

---

**Xem chi tiết:** [README_MYSQL.md](README_MYSQL.md)