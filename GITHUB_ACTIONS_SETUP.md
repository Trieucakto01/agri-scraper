# 🚀 GitHub Actions Setup Guide

Hướng dẫn setup automatic scraper với PHP API trên GitHub Actions.

## ✅ Điều kiện tiên quyết

- Repository trên GitHub
- Quyền admin để thay đổi Settings
- File `gianongsan1.php` đã upload lên server
- File `.github/workflows/scrape.yml` đã có

## 📝 Step-by-Step Setup

### Step 1: Mở Repository Settings

1. Vào repo của bạn trên GitHub
2. Click **Settings** tab (góc trên phải)
3. Click **Secrets and variables** (sidebar trái)
4. Click **Actions** submenu

### Step 2: Thêm Secrets

#### 2.1 Thêm SECRET_KEY
1. Click **New repository secret**
2. Name: `SECRET_KEY`
3. Value: `ditmecuocdoi`
4. Click **Add secret**

#### 2.2 Thêm PHP_ENDPOINT
1. Click **New repository secret**
2. Name: `PHP_ENDPOINT`
3. Value: `https://agriht.com/gianongsan1.php`
4. Click **Add secret**

✅ Kết quả: 2 secrets được tạo

```
Secrets:
├── SECRET_KEY = ditmecuocdoi (masked)
└── PHP_ENDPOINT = https://agriht.com/gianongsan1.php (masked)
```

### Step 3: Upload PHP File

**⚠️ QUAN TRỌNG:** Upload file `gianongsan1.php` lên server trước:

1. Mở Hostinger File Manager (hoặc dùng FTP)
2. Upload `gianongsan1.php` vào `public_html/`
3. Chỉnh sửa file, cập nhật MySQL password:
  ```php
  define('DB_PASS', 'YOUR_ACTUAL_PASSWORD');
  ```
4. Save file
5. Test endpoint: `curl -X POST -H "X-Secret-Key: ditmecuocdoi" https://agriht.com/gianongsan1.php`

### Step 4: Xác minh Workflow
1. Vào repo, click **Actions** tab (top)
2. Left sidebar: Xem **"Cập Nhật Giá Nông Sản"** (nếu được list)
3. Nếu chưa thấy, push code lên main branch

### Step 5: Test Workflow

#### Option A: Trigger Manual Run
1. Click **"Cập Nhật Giá Nông Sản"** workflow
2. Click **Run workflow** (nút bên phải)
3. Confirm: **Run workflow**
4. ✅ Yellow dot = running, Green checkmark = success

#### Option B: Push Code Trigger
```bash
git add .
git commit -m "Revert to PHP API with SECRET_KEY"
git push origin main
```
Workflow sẽ trigger tự động.

## 📊 Monitor Workflow

### Xem Status
1. **Actions** tab → **"Cập Nhật Giá Nông Sản"**
2. Xem các run histories
3. Click run để xem chi tiết logs

### Xem Logs
1. Click vào một workflow run
2. Job: **scrape-and-update**
3. Expand steps để xem output
4. Look for: ✅ hoặc ❌ status

### Artifacts
1. Scroll down workflow run page
2. **Artifacts** section
3. Download `screenshot-XXX.png` nếu lỗi OCR

## 🔄 Scheduling

Workflow tự động chạy:
- **Mỗi 6 giờ** (cron schedule)
- Lúc: 00:00, 06:00, 12:00, 18:00 UTC
- Có thể thay đổi cron trong `.github/workflows/scrape.yml`:

```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours
  # Ví dụ khác:
  # - cron: '0 8 * * *'  # Every day at 8 AM
  # - cron: '0 * * * *'  # Every hour
```

**Lưu ý**: UTC timezone, không phải giờ địa phương

## 📧 Notifications

### Email Notifications
GitHub tự động gửi email nếu:
- ✅ Workflow thành công
- ❌ Workflow thất bại

Để bật/tắt:
1. **Settings** → **Notifications**
2. Check/uncheck **Actions**

### Webhook Notifications
Để tích hợp Slack, Discord, v.v.:
1. Tạo webhook URL từ platform
2. Thêm Secret: `WEBHOOK_URL`
3. Update workflow để gửi notification

```yaml
- name: Notify on failure
  if: failure()
  run: |
    curl -X POST ${{ secrets.WEBHOOK_URL }} \
      -H 'Content-Type: application/json' \
      -d '{"text":"Scraper failed!"}'
```

## 🐛 Troubleshooting

### ❌ Workflow không chạy

**Nguyên nhân**: Secrets không được set
**Fix**: 
1. Kiểm tra Step 2 (thêm SECRET_KEY + PHP_ENDPOINT)
2. Ensure không có spaces trước/sau values
3. Re-test manual run

### ❌ "Unauthorized" error

**Nguyên nhân**: SECRET_KEY sai
**Fix**:
1. Xác nhận SECRET_KEY = `ditmecuocdoi`
2. Xóa secret, tạo lại
3. Push code để trigger lại

### ❌ "Chrome not found"

**Nguyên nhân**: Chrome không cài trong GitHub Actions runner
**Fix**: 
```yaml
- uses: browser-actions/setup-chrome@latest
  with:
    chrome-version: stable
```

(Đã thêm vào workflow rồi, không cần lo)

### ❌ reCAPTCHA still blocking

**Nguyên nhân**: undetected-chromedriver version lỗi
**Fix**:
```bash
pip install --upgrade undetected-chromedriver
git push
```

### ⏱️ Workflow timeout

**Nguyên nhân**: Script chạy quá 6 giờ (default timeout)
**Fix**: 
```yaml
timeout-minutes: 30  # Tăng timeout
```

## 📊 Performance Tips

1. **Cache dependencies**: GitHub tự động cache pip packages
2. **Parallel jobs**: Hiện tại chỉ 1 job, có thể scale to multiple jobs
3. **Optimize OCR**: Resize hình trước OCR để tăng tốc

## 🔐 Security Best Practices

1. ✅ Secrets được mã hóa (không hiển thị logs)
2. ✅ Dùng `${{ secrets.SECRET_KEY }}` trong workflow
3. ✅ KHÔNG paste secrets ở chỗ khác
4. ✅ Rotate secrets định kỳ (3-6 tháng)

## 🚀 Advanced Setup

### Trigger from Webhook
```bash
# POST to GitHub workflow
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/Trieucakto01/agri-scraper/dispatches \
  -d '{"event_type":"trigger-scraper"}'
```

### Custom Schedule
Modify `.github/workflows/scrape.yml`:
```yaml
schedule:
  - cron: '0 8 * * MON-FRI'  # Weekdays 8 AM UTC
```

### Slack Notifications
```yaml
- uses: slackapi/slack-github-action@v1
  if: always()
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
```

## ✅ Verification Checklist

- [ ] Repository exists on GitHub
- [ ] `.github/workflows/scrape.yml` file present
- [ ] SECRET_KEY secret added
- [ ] PHP_ENDPOINT secret added
- [ ] Manual workflow run successful
- [ ] Artifacts generated (if any)
- [ ] Logs show "✅ HOÀN THÀNH"
- [ ] Database updated with new prices

## 📚 Resources

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Cron Schedule Helper](https://crontab.guru/)
- [undetected-chromedriver Docs](https://github.com/ultrafunkamsterdam/undetected-chromedriver)

## 🎯 Next Steps

1. ✅ Setup secrets (Step 1-2)
2. ✅ Test manual run (Step 4-A)
3. ✅ Push code to automate
4. 📊 Monitor workflow runs
5. 🎉 Success! Auto-updates every 6 hours

---

**Support**: Check logs in Actions tab for detailed error messages.
