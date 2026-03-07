# Quay lại cách PHP API với SECRET_KEY

**Ngày:** 6 tháng 3, 2026  
**Trạng thái:** ✅ HOÀN THÀNH

## 🔄 Thay đổi

### Kiến trúc CŨ (Direct MySQL)
```
GitHub Actions → Python → Direct MySQL connection
```
**Vấn đề:** Có thể bị chặn bởi firewall, cần whitelist IP GitHub Actions

### Kiến trúc MỚI (PHP API)
```
GitHub Actions → Python → POST to PHP API (with SECRET_KEY) → MySQL
```
**Lợi ích:** 
- ✅ Không cần whitelist IP
- ✅ Có authentication layer (SECRET_KEY)
- ✅ Dễ deploy trên shared hosting (Hostinger)
- ✅ PHP xử lý MySQL connection locally

## 📝 Các file đã thay đổi

### 1. scrape_giacaphe.py
- ❌ Xóa: `import mysql.connector`
- ✅ Thêm: `import requests`
- ❌ Xóa: `DB_CONFIG` dict với MySQL credentials
- ✅ Thêm: `PHP_ENDPOINT` và `SECRET_KEY`
- ❌ Xóa: `insert_to_db()` function
- ✅ Thêm: `post_to_php()` function

### 2. update_gianongsan.py
- ✅ Import `post_to_php` thay vì `insert_to_db`
- ✅ Gọi `post_to_php(records)` thay vì `insert_to_db(records)`
- ✅ Cập nhật log messages

### 3. .env.example
```diff
- DB_HOST=153.92.15.31
- DB_PORT=3306
- DB_USER=u697673786_Agriht
- DB_PASSWORD=
- DB_NAME=u697673786_Agriht
+ SECRET_KEY=ditmecuocdoi
+ PHP_ENDPOINT=https://agriht.com/gianongsan1.php
```

### 4. .github/workflows/scrape.yml
- ❌ Xóa: Preflight network diagnostics step
- ❌ Xóa: MySQL login test step
- ✅ Cập nhật: Dùng `SECRET_KEY` và `PHP_ENDPOINT` trong env

### 5. requirements.txt
- ❌ Xóa: `mysql-connector-python`
- ✅ Giữ: `requests` (đã có sẵn)

### 6. gianongsan1.php (MỚI)
- ✅ PHP API endpoint nhận POST requests
- ✅ Xác thực bằng `X-Secret-Key` header
- ✅ Tự động tạo table `gia_nong_san` nếu chưa có
- ✅ INSERT ... ON DUPLICATE KEY UPDATE
- ✅ Response JSON với `inserted`, `updated`, `errors`

### 7. README.md
- ✅ Cập nhật hướng dẫn setup
- ✅ Thay `test_mysql.py` → `test_post.py`
- ✅ Cập nhật troubleshooting
- ✅ Thêm hướng dẫn upload PHP file

### 8. GITHUB_ACTIONS_SETUP.md
- ✅ Cập nhật secrets: SECRET_KEY và PHP_ENDPOINT
- ✅ Thêm bước upload PHP file lên server

## 🚀 Cách sử dụng

### Local Testing
```bash
# 1. Tạo .env file
cp .env.example .env

# 2. Cập nhật .env
# SECRET_KEY=ditmecuocdoi
# PHP_ENDPOINT=https://agriht.com/gianongsan1.php

# 3. Test PHP endpoint
python test_post.py

# 4. Chạy scraper
python update_gianongsan.py
```

### GitHub Actions Setup
1. **Upload PHP file:**
   - Upload `gianongsan1.php` lên `public_html/` trên Hostinger
   - Cập nhật MySQL password trong PHP file
   
2. **Add GitHub Secrets:**
   - `SECRET_KEY` = `ditmecuocdoi`
   - `PHP_ENDPOINT` = `https://agriht.com/gianongsan1.php`
   
3. **Run workflow:**
   - Manual: Actions → Run workflow
   - Auto: Tự chạy mỗi 6 giờ

## 📋 Checklist

- [x] Cập nhật scrape_giacaphe.py với post_to_php()
- [x] Cập nhật update_gianongsan.py
- [x] Cập nhật .env.example
- [x] Cập nhật GitHub Actions workflow
- [x] Tạo gianongsan1.php
- [x] Cập nhật requirements.txt
- [x] Cập nhật README.md
- [x] Cập nhật GITHUB_ACTIONS_SETUP.md

## ⚠️ Bước tiếp theo (cần làm thủ công)

1. **Upload gianongsan1.php lên server:**
   ```bash
   # Dùng FTP hoặc Hostinger File Manager
   # Upload vào: public_html/gianongsan1.php
   ```

2. **Cập nhật MySQL password trong gianongsan1.php:**
   ```php
   define('DB_PASS', 'YOUR_ACTUAL_PASSWORD');
   ```

3. **Test PHP endpoint:**
   ```bash
   curl -X POST \
     -H "Content-Type: application/json" \
     -H "X-Secret-Key: ditmecuocdoi" \
     -d '[{"ngay_cap_nhat":"2026-03-06","san_pham":"Cà phê","thi_truong":"Test","gia_trung_binh":96000,"thay_doi":0,"ty_gia_usd_vnd":25300,"cap_nhat_luc":"10:00:00"}]' \
     https://agriht.com/gianongsan1.php
   ```

4. **Add GitHub Secrets:**
   - Repository → Settings → Secrets → Actions
   - Thêm `SECRET_KEY` và `PHP_ENDPOINT`

5. **Test workflow:**
   - Actions → Cập Nhật Giá Nông Sản → Run workflow

## 🎯 Kết quả mong đợi

✅ GitHub Actions → POST to PHP → MySQL insert thành công  
✅ Không cần whitelist IP  
✅ Có authentication với SECRET_KEY  
✅ Workflow chạy tự động mỗi 6 giờ
