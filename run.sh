#!/bin/bash
# run.sh - Script chạy nhanh để cập nhật giá nông sản

set -e

# Load biến môi trường từ .env nếu có
if [ -f .env ]; then
    echo "📝 Load biến môi trường từ .env"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Kiểm tra SECRET_KEY
if [ -z "$SECRET_KEY" ]; then
    echo "❌ Thiếu SECRET_KEY!"
    echo "Tạo file .env hoặc export SECRET_KEY='ditmecuocdoi'"
    exit 1
fi

# Kiểm tra dependencies
if ! command -v tesseract &> /dev/null; then
    echo "❌ Tesseract chưa cài!"
    echo "Chạy: sudo apt-get install tesseract-ocr tesseract-ocr-vie"
    exit 1
fi

if ! python -c "import playwright" 2>/dev/null; then
    echo "❌ Playwright chưa cài!"
    echo "Chạy: pip install -r requirements.txt && playwright install chromium"
    exit 1
fi

echo "🚀 Bắt đầu cập nhật giá nông sản..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python update_gianongsan.py
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Hoàn thành!"
