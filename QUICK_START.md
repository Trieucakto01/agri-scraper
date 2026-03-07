# 🚀 Quick Start - Selenium Bypass reCAPTCHA

## ⚡ Cài đặt nhanh (3 bước)

### 1️⃣ Cài Chrome
```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y google-chrome-stable

# macOS
brew install google-chrome
```

### 2️⃣ Cài Python packages
```bash
pip install -r requirements.txt
```

### 3️⃣ Test Selenium
```bash
export SECRET_KEY='ditmecuocdoi'
export PHP_ENDPOINT='https://agriht.com/gianongsan1.php'
python test_selenium.py
```

## ✅ Nếu thành công
```
✅ THÀNH CÔNG
  - Inserted: 2
  - Updated: 0
```

## 🎯 Chạy scraper chính
```bash
python update_gianongsan.py
```

## 📝 Variables cần export
```bash
export SECRET_KEY='ditmecuocdoi'           # Bắt buộc
export PHP_ENDPOINT='https://agriht.com/gianongsan1.php'  # Optional
```

## 💡 Nếu lỗi
- **"Chrome not found"** → Cài Chrome (bước 1)
- **"Module not found"** → Cài packages (bước 2)
- **"Unauthorized"** → Kiểm tra SECRET_KEY
- **"reCAPTCHA timeout"** → Website quá tải, thử lại sau

## 🔧 Xem chi tiết
Xem [SELENIUM_SETUP.md](SELENIUM_SETUP.md) để cấu hình nâng cao.
