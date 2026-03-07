# OneSignal Integration - Summary

**Ngày:** 6 tháng 3, 2026  
**Trạng thái:** ✅ HOÀN THÀNH

## 🎯 Tính năng mới

Sau khi scrape và cập nhật giá nông sản thành công, hệ thống tự động:
- ✅ Gửi push notification qua OneSignal
- ✅ Hiển thị top 5 sản phẩm có biến động giá nhiều nhất
- ✅ Khi tap vào thông báo → mở `https://agriht.com/gia-nong-san/`
- ✅ Tùy chọn: Nếu không config OneSignal, scraper vẫn chạy bình thường

## 📝 Files thay đổi

### 1. scrape_giacaphe.py
**Thêm:**
- OneSignal configuration (ONESIGNAL_APP_ID, ONESIGNAL_REST_API_KEY)
- Function `send_onesignal_notification(records)` 
  - Format message với top 5 sản phẩm
  - POST tới OneSignal API
  - Handle errors gracefully
- Gọi `send_onesignal_notification()` sau khi `post_to_php()` thành công

### 2. .env.example
**Thêm:**
```env
ONESIGNAL_APP_ID=
ONESIGNAL_REST_API_KEY=
```

### 3. .github/workflows/scrape.yml
**Thêm env variables:**
```yaml
env:
  ONESIGNAL_APP_ID: ${{ secrets.ONESIGNAL_APP_ID }}
  ONESIGNAL_REST_API_KEY: ${{ secrets.ONESIGNAL_REST_API_KEY }}
```

### 4. README.md
**Cập nhật:**
- Thêm OneSignal vào GitHub Actions Secrets
- Thêm biến môi trường OneSignal
- Thêm `test_onesignal.py` vào hướng dẫn test
- Thêm link tới ONESIGNAL_SETUP.md
- Cập nhật File Structure

### 5. test_onesignal.py (MỚI)
**Script test OneSignal:**
- Gửi thông báo test với dữ liệu mẫu
- Kiểm tra credentials
- Hiển thị số recipients
- Error handling và troubleshooting tips

### 6. ONESIGNAL_SETUP.md (MỚI)
**Tài liệu chi tiết:**
- Hướng dẫn tạo OneSignal app
- Lấy App ID và REST API Key
- Cấu hình local và GitHub Actions
- Test và troubleshooting
- Thêm OneSignal SDK vào website

## 📋 Format thông báo

```
Tiêu đề: 🌾 Giá Nông Sản Mới

Nội dung:
Giá nông sản hôm nay có sự biến động như sau:
Đắk Lắk 96.000 +1.200
Lâm Đồng 95.500 +1.300
Gia Lai 96.000 +1.200
Đắk Nông 96.000 +1.000
Hồ tiêu 146.000 +2.000

URL: https://agriht.com/gia-nong-san/
```

## 🚀 Cách sử dụng

### Local Test
```bash
# 1. Cấu hình OneSignal credentials
export ONESIGNAL_APP_ID='your-app-id'
export ONESIGNAL_REST_API_KEY='your-api-key'

# 2. Test OneSignal
python test_onesignal.py

# 3. Chạy scraper full (sẽ gửi thông báo sau khi POST thành công)
python update_gianongsan.py
```

### GitHub Actions
```bash
# 1. Vào GitHub repo → Settings → Secrets
# 2. Thêm 2 secrets:
#    - ONESIGNAL_APP_ID
#    - ONESIGNAL_REST_API_KEY
# 3. Run workflow → Tự động gửi thông báo
```

## 🔧 Code Logic

```python
# Trong scrape_giacaphe.py

def post_to_php(records):
    # ... POST tới PHP endpoint ...
    
    if response.status_code == 200:
        # ... log success ...
        
        # Gửi thông báo OneSignal
        send_onesignal_notification(records)

def send_onesignal_notification(records):
    # Check credentials
    if not ONESIGNAL_APP_ID or not ONESIGNAL_REST_API_KEY:
        log.warning("OneSignal không được cấu hình, bỏ qua")
        return
    
    # Sort records by price change
    sorted_records = sorted(records, key=lambda x: abs(x['thay_doi']), reverse=True)
    top_records = sorted_records[:5]
    
    # Format message
    message = "Giá nông sản hôm nay có sự biến động như sau:\n"
    for rec in top_records:
        message += f"{rec['thi_truong']} {rec['gia_trung_binh']:,.0f} {rec['thay_doi']:+,.0f}\n"
    
    # POST to OneSignal API
    # ...
```

## ⚠️ Lưu ý

1. **Tùy chọn:** OneSignal là optional
   - Nếu không config → Log warning và bỏ qua
   - Không làm fail scraper

2. **Credentials bảo mật:**
   - Không commit App ID/API Key vào Git
   - Lưu trong `.env` (local) hoặc GitHub Secrets

3. **Website integration:**
   - Cần thêm OneSignal SDK vào website
   - User phải subscribe để nhận thông báo
   - Xem ONESIGNAL_SETUP.md bước 6

4. **Testing:**
   - Dùng `test_onesignal.py` để test trước
   - Không cần chạy full scraper để test

## 📊 Expected Output

### Logs khi có OneSignal:
```
📡 POST tới: https://agriht.com/gianongsan1.php
✅ Hoàn thành!
  - Inserted: 12
  - Updated: 3
📢 Gửi thông báo OneSignal...
✅ Đã gửi thông báo tới 42 thiết bị
```

### Logs khi không có OneSignal:
```
📡 POST tới: https://agriht.com/gianongsan1.php
✅ Hoàn thành!
  - Inserted: 12
  - Updated: 3
⚠️  OneSignal không được cấu hình, bỏ qua thông báo
```

## ✅ Checklist

- [x] Thêm OneSignal config vào scrape_giacaphe.py
- [x] Tạo function send_onesignal_notification()
- [x] Gọi function sau khi POST thành công
- [x] Cập nhật .env.example
- [x] Cập nhật GitHub Actions workflow
- [x] Tạo test_onesignal.py
- [x] Tạo ONESIGNAL_SETUP.md
- [x] Cập nhật README.md
- [x] Test syntax (no errors)

## 🎯 Bước tiếp theo (người dùng làm)

1. **Tạo OneSignal App:**
   - Vào https://onesignal.com/
   - Tạo app mới
   - Lấy App ID và REST API Key

2. **Cấu hình Local:**
   - Thêm vào `.env`:
     ```
     ONESIGNAL_APP_ID=...
     ONESIGNAL_REST_API_KEY=...
     ```

3. **Test:**
   ```bash
   python test_onesignal.py
   ```

4. **Cấu hình GitHub:**
   - Add 2 secrets: ONESIGNAL_APP_ID, ONESIGNAL_REST_API_KEY

5. **Thêm SDK vào website:**
   - Copy code từ OneSignal Dashboard
   - Paste vào `<head>` của agriht.com

6. **Subscribe và test:**
   - Mở website
   - Allow notifications
   - Chạy scraper → Nhận thông báo

Xem chi tiết: **ONESIGNAL_SETUP.md**
