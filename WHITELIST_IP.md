# 🔐 Whitelist IP cho MySQL Remote Connection

## Vấn đề hiện tại
PHP endpoint `gianongsan1.php` bị **LiteSpeed Bot Protection** chặn với reCAPTCHA.

**Giải pháp:** Kết nối trực tiếp MySQL (bypass web server)

## Bước 1: Lấy IP cần whitelist

### GitHub Actions IP
GitHub Actions sử dụng nhiều IP khác nhau, nên cần whitelist all:

```
0.0.0.0/0
```

Hoặc ranges cụ thể:
```
4.175.114.51
13.64.0.0/11  
20.20.0.0/16
```

### Codespace IP (để test local)
```bash
curl https://api.ipify.org
```
**IP hiện tại:** `207.46.224.82`

## Bước 2: Whitelist trên Hostinger

1. Login vào **Hostinger Control Panel**: https://hpanel.hostinger.com
2. Chọn hosting: **agriht.com**
3. Vào **Databases** → **MySQL Databases**
4. Tìm database: `u697673786_Agriht`
5. Scroll xuống phần **"Remote MySQL"**
6. Click **"Add New IP"**
7. Nhập: `0.0.0.0/0` (allow all)
8. Click **Save**

## Bước 3: Test kết nối

```bash
python test_mysql.py
```

**Expected output:**
```
✅ Kết nối thành công!
MySQL Version: 8.0.x
✅ Table sẵn sàng
✅ Chèn/cập nhật xong: 2 inserted, 0 updated
```

## Bước 4: Chạy scraper

```bash
python update_gianongsan.py
```

---

## Lưu ý bảo mật

⚠️ **Cho phép 0.0.0.0/0 có rủi ro bảo mật** (ai cũng có thể kết nối nếu biết password)

**Bảo vệ:**
- ✅ Đã có: Strong password (`Toilatyphu1ty@`)
- ✅ Đã có: Database có user/pass riêng
- ✅ Script không public password trong logs
- ✅ GitHub Secrets ẩn credentials

**Nếu lo lắng về bảo mật:**
- Chỉ whitelist GitHub Actions IPs cụ thể (nhưng có thể thay đổi)
- Hoặc dùng VPN/Proxy với static IP
