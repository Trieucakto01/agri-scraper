# 🌾 Agri Scraper - Cập Nhật Giá Tự Động (Direct MySQL)

Script Python để scrape và cập nhật giá nông sản (cà phê, tiêu) **trực tiếp vào MySQL database** mà không cần qua HTTP endpoint.

## 📋 Kiến Trúc

```
giacaphe.com (giá cà phê)
         ↓
    Playwright (screenshot)
         ↓
    Tesseract OCR (parse)
         ↓
    MySQL Database ← Direct Connection (bypass Bot Protection)
```

**Lợi ích:**
- ✅ Bypass Cloudflare Bot Protection (không cần reCAPTCHA)
- ✅ Nhanh hơn (không qua HTTP layer)
- ✅ Đơn giản hơn (không cần PHP endpoint)

## 🚀 Setup

### 1. Clone & Install

```bash
git clone <repo>
cd agri-scraper
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# hoặc: .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Cấu Hình MySQL (Hostinger)

#### Lấy MySQL Credentials từ Hostinger

1. Vào **Hostinger Control Panel**
2. Chọn **Databases** → **MySQL**
3. Tìm hoặc tạo Remote MySQL User:
   - **Host**: `xxx.hostinger.com` (hoặc IP)
   - **User**: `u697673786_*` (username)
   - **Password**: (set hoặc reset)
   - **Database**: `u697673786_*` (database name)

4. **Thêm IP của GitHub Actions** (nếu cần):
   - Vào **Remote MySQL** settings
   - Add IP: `0.0.0.0/0` (allow all) HOẶC GitHub Actions IPs

#### Tạo file `.env`

```bash
cp .env.example .env
```

Edit `.env`:

```env
DB_HOST=xxx.hostinger.com
DB_USER=u697673786_username
DB_PASSWORD=your_password_here
DB_NAME=u697673786_agriht
```

### 3. Test MySQL Connection

```bash
source .venv/bin/activate
python test_mysql.py
```

Expected output:
```
✅ Kết nối thành công!
MySQL Version: 8.0.x
✅ Table sẵn sàng
✅ Chèn/cập nhật xong: 2 inserted, 0 updated
```

## 📝 Sử Dụng

### Test OCR & Scrape

```bash
python scrape_giacaphe.py  # Chỉ chup + OCR, không insert DB
```

### Chạy Full Workflow (Scrape + Insert)

```bash
source .venv/bin/activate
python update_gianongsan.py
```

Output:
```
✅ Đã parse được 12 bản ghi
[3/3] Đang lưu dữ liệu vào MySQL...
✅ Hoàn thành!
  - Inserted: 8
  - Updated: 4
```

## ⚙️ GitHub Actions Setup

### 1. Add Secrets

Repository → **Settings** → **Secrets and variables** → **Actions**

Thêm 4 secrets:

| Secret Name | Value |
|-------------|-------|
| `DB_HOST` | `xxx.hostinger.com` |
| `DB_USER` | `u697673786_username` |
| `DB_PASSWORD` | `your_password` |
| `DB_NAME` | `u697673786_agriht` |

### 2. Workflow Configuration

`.github/workflows/scrape.yml`:

```yaml
on:
  schedule:
    - cron: '0 */6 * * *'  # Chạy 4 lần/ngày (0, 6, 12, 18 giờ)
```

### 3. Trigger Manual Run

**Actions** → **"Cập Nhật Giá Nông Sản"** → **Run workflow**

## 📊 Database Schema

Tự động tạo khi chạy script lần đầu:

```sql
CREATE TABLE gia_nong_san (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    ngay_cap_nhat   DATE          NOT NULL,
    san_pham        VARCHAR(50)   NOT NULL,
    thi_truong      VARCHAR(100)  NOT NULL,
    gia_trung_binh  DECIMAL(15,2) DEFAULT 0,
    thay_doi        DECIMAL(10,2) DEFAULT 0,
    ty_gia_usd_vnd  DECIMAL(15,2) DEFAULT 0,
    cap_nhat_luc    TIME,
    UNIQUE KEY uq_ngay_sp_tt (ngay_cap_nhat, san_pham, thi_truong)
) ENGINE=InnoDB CHARSET=utf8mb4
```

## 📁 Cấu Trúc

```
agri-scraper/
├── .github/
│   └── workflows/scrape.yml    # GitHub Actions (mỗi 6h)
├── scrape_giacaphe.py          # Main: Playwright + OCR + MySQL
├── update_gianongsan.py        # Wrapper orchestration
├── test_mysql.py               # Test MySQL connection
├── requirements.txt            # Dependencies
├── .env.example                # Environment template
└── README_MYSQL.md             # Documentation (này)
```

## 🔍 Troubleshooting

### ❌ "Can't connect to MySQL server"

**Kiểm tra:**

1. **MySQL credentials đúng?**
   ```bash
   echo $DB_HOST $DB_USER
   ```

2. **Firewall/Port mở?**
   ```bash
   telnet xxx.hostinger.com 3306
   ```

3. **IP được phép?**
   - Vào Hostinger: Remote MySQL settings
   - Add GitHub IP hoặc `0.0.0.0/0`

4. **Database tồn tại?**
   ```bash
   # Kiểm tra trong Hostinger Control Panel → Databases
   ```

### ❌ "Access denied for user"

- Kiểm tra password trong `.env`
- Reset MySQL password trong Hostinger
- Đảm bảo user có **INSERT/UPDATE privileges**

### ❌ "Table doesn't exist"

Script tự động tạo. Nếu error vẫn xuất hiện:

```bash
# Manual create:
mysql -h $DB_HOST -u $DB_USER -p $DB_NAME < schema.sql
```

### ⚠️ OCR kết quả sai

- Tesseract cần Vietnamese language pack:
  ```bash
  sudo apt-get install tesseract-ocr-vie  # Linux
  # Mac: brew install tesseract
  # Windows: https://github.com/UB-Mannheim/tesseract/wiki
  ```

- Nếu vẫn sai, check `scrape_giacaphe.py` → `ocr_bang_gia()` function

## 📦 Dependencies

```
playwright          # Browser automation
pillow             # Image processing
pytesseract        # OCR Vietnamese
mysql-connector-python  # MySQL connection
```

## 📝 Environment Variables

| Variable | Default | Note |
|----------|---------|------|
| `DB_HOST` | `localhost` | MySQL server hostname |
| `DB_USER` | `root` | MySQL username |
| `DB_PASSWORD` | `` | MySQL password |
| `DB_NAME` | `agriht` | Database name |

Load từ `.env` hoặc set:

```bash
export DB_HOST=xxx.hostinger.com
export DB_USER=u697673786_user
export DB_PASSWORD=password123
export DB_NAME=u697673786_agriht
```

## 🔒 Security Notes

- ⚠️ **Không commit `.env` file!** (đã thêm `.gitignore`)
- ⚠️ **GitHub Secrets:** Use only for production deployment
- ⚠️ **Database User:** Limit privileges to INSERT/UPDATE on `gia_nong_san` table only

## 🎯 Next Steps

1. ✅ Setup MySQL connection testing
2. ✅ Test locally: `python test_mysql.py`
3. ✅ Run workflow: `python update_gianongsan.py`
4. ✅ Add GitHub Secrets
5. ✅ Schedule workflow (every 6 hours)
6. ✅ Monitor Actions tab for runs

## 📞 Support

- Check **Actions** tab for error logs
- Review `test_mysql.py` output for connection issues
- Verify Hostinger MySQL Remote Access settings

---

**Last Updated:** March 2026  
**Status:** ✅ Direct MySQL (Bypass Bot Protection)
