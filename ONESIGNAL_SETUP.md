# 📢 OneSignal Push Notification Setup

Hướng dẫn cấu hình OneSignal để gửi thông báo giá nông sản tới người dùng.

## 🎯 Tính năng

Sau khi scrape và cập nhật giá thành công, hệ thống tự động:
- ✅ Gửi thông báo push tới tất cả thiết bị đã subscribe
- ✅ Hiển thị top 5 sản phẩm có biến động giá nhiều nhất
- ✅ Format: `Đắk Lắk 96,000 +1,200`
- ✅ Khi tap vào thông báo → mở `https://agriht.com/gia-nong-san/`

## 📝 Bước 1: Tạo OneSignal App

### 1.1 Đăng ký OneSignal
1. Vào https://onesignal.com/
2. Đăng ký tài khoản miễn phí
3. Click **New App/Website**

### 1.2 Chọn Platform
1. Chọn **Website Push**
2. Nhập tên app: `Agriht - Giá Nông Sản`
3. Click **Next**

### 1.3 Cấu hình Website
1. **Site URL:** `https://agriht.com`
2. **Auto Resubscribe:** Enabled (khuyến nghị)
3. **Default Notification Icon:** Upload logo (512x512px khuyến nghị)
4. Click **Save**

## 🔑 Bước 2: Lấy API Keys

### 2.1 App ID
1. Vào OneSignal Dashboard
2. Click vào app vừa tạo
3. **Settings** → **Keys & IDs**
4. Copy **OneSignal App ID**
   - Ví dụ: `12345678-1234-1234-1234-123456789012`

### 2.2 REST API Key
1. Cùng trang **Keys & IDs**
2. Tìm **REST API Key** (không phải User Auth Key!)
3. Click **Copy** 
   - Format đúng: Dài khoảng 40-50 ký tự
   - Ví dụ: `MGFhNjJkYmItZjM5Yi00MjMwLWEwNDUtYjJhZDYzYzQ1NzUy`
   - ⚠️ **LƯU Ý:** Nếu không thấy REST API Key, vào **Settings → Keys & IDs → REST API Key → Generate New Key**

## ⚙️ Bước 3: Cấu hình Local

### 3.1 Tạo file .env
```bash
cp .env.example .env
```

### 3.2 Thêm OneSignal credentials
Sửa file `.env`:
```env
SECRET_KEY=ditmecuocdoi
PHP_ENDPOINT=https://agriht.com/gianongsan1.php

# OneSignal
ONESIGNAL_APP_ID=12345678-1234-1234-1234-123456789012
ONESIGNAL_REST_API_KEY=NGFhNjJkYmItZjM5Yi00MjMwLWEwNDUtYjJhZDYzYzQ1NzUy
```

## 🚀 Bước 4: Cấu hình GitHub Actions

### 4.1 Thêm Secrets
1. Vào GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Thêm 2 secrets:

**Secret 1:**
- Name: `ONESIGNAL_APP_ID`
- Value: `12345678-1234-1234-1234-123456789012` (thay bằng App ID thật)

**Secret 2:**
- Name: `ONESIGNAL_REST_API_KEY`
- Value: `NGFhNjJkYmItZjM5Yi00MjMwLWEwNDUtYjJhZDYzYzQ1NzUy` (thay bằng REST API Key thật)

✅ Kết quả: 4 secrets
```
Secrets:
├── SECRET_KEY
├── PHP_ENDPOINT
├── ONESIGNAL_APP_ID
└── ONESIGNAL_REST_API_KEY
```

## 🧪 Bước 5: Test

### 5.1 Test Local
```bash
python update_gianongsan.py
```

Xem logs:
```
📢 Gửi thông báo OneSignal...
✅ Đã gửi thông báo tới 42 thiết bị
```

### 5.2 Test GitHub Actions
1. Vào repo → **Actions** tab
2. Click workflow **"Cập Nhật Giá Nông Sản"**
3. Click **Run workflow**
4. Xem logs step **"Run scraper"**

## 📱 Bước 6: Thêm Subscribers

### 6.1 Thêm OneSignal SDK vào Website
Vào OneSignal Dashboard:
1. **Settings** → **Platforms** → **Web Push**
2. Copy code snippet
3. Paste vào `<head>` của website `agriht.com`

Example code:
```html
<script src="https://cdn.onesignal.com/sdks/OneSignalSDK.js" async=""></script>
<script>
  window.OneSignal = window.OneSignal || [];
  OneSignal.push(function() {
    OneSignal.init({
      appId: "12345678-1234-1234-1234-123456789012",
    });
  });
</script>
```

### 6.2 Test Subscribe
1. Mở website `https://agriht.com` trên trình duyệt
2. Nhấn **Allow** khi browser hỏi quyền notifications
3. Vào OneSignal Dashboard → **Audience** → **All Users**
4. Xem số lượng Subscribed Users tăng lên

## 📊 Format Thông Báo

### Tiêu đề (Heading)
```
Giá Nông Sản Mới
```

### Nội dung (Message)
```
Giá nông sản hôm nay có sự biến động như sau:
Đắk Lắk 96,000 +1,200
Lâm Đồng 95,500 +1,300
Gia Lai 96,000 +1,200
Đắk Nông 96,000 +1,000
Hồ tiêu 146,000 +2,000
```

### URL khi tap
```
https://agriht.com/gia-nong-san/
```

## 🐛 Troubleshooting

### ⚠️ "OneSignal không được cấu hình, bỏ qua thông báo"
- Thiếu `ONESIGNAL_APP_ID` hoặc `ONESIGNAL_REST_API_KEY`
- Kiểm tra `.env` file (local) hoặc GitHub Secrets
- **Lưu ý:** Nếu không cần OneSignal, để trống là được (không ảnh hưởng scraper)

### ❌ "OneSignal error 400"
- App ID hoặc REST API Key sai
- Vào OneSignal Dashboard → Settings → Keys & IDs để kiểm tra lại

### 📭 "Đã gửi thông báo tới 0 thiết bị"
- Chưa có ai subscribe notifications
- Thêm OneSignal SDK vào website (Bước 6)
- Hoặc test bằng OneSignal Test Device

### 🧪 Test với OneSignal Test User
1. OneSignal Dashboard → **Audience** → **Test Users**
2. Add test user/device
3. Chạy scraper và xem thông báo trên device

## 🔒 Bảo mật

- ✅ REST API Key phải giữ bí mật (không commit vào Git)
- ✅ Chỉ lưu trong `.env` (local) và GitHub Secrets
- ✅ `.gitignore` đã bỏ qua file `.env`

## 📚 Tài liệu tham khảo

- [OneSignal Web Push Quickstart](https://documentation.onesignal.com/docs/web-push-quickstart)
- [OneSignal REST API](https://documentation.onesignal.com/reference/create-notification)
- [OneSignal Dashboard](https://app.onesignal.com/)

## 🎯 Tóm tắt

1. ✅ Tạo app trên OneSignal.com
2. ✅ Lấy App ID và REST API Key
3. ✅ Thêm vào `.env` (local) và GitHub Secrets
4. ✅ Thêm OneSignal SDK vào website
5. ✅ Chạy scraper → Tự động gửi thông báo
