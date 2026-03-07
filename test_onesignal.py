#!/usr/bin/env python3
"""
test_onesignal.py
Script test để gửi thông báo OneSignal mẫu
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import requests
import logging
import base64
from datetime import date

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# OneSignal Configuration
ONESIGNAL_APP_ID = os.environ.get("ONESIGNAL_APP_ID", "")
ONESIGNAL_REST_API_KEY = os.environ.get("ONESIGNAL_REST_API_KEY", "")
ONESIGNAL_URL = "https://onesignal.com/api/v1/notifications"

def test_onesignal():
    """Gửi thông báo OneSignal test"""
    
    log.info("=" * 60)
    log.info("TEST ONESIGNAL PUSH NOTIFICATION")
    log.info("=" * 60)
    
    if not ONESIGNAL_APP_ID or not ONESIGNAL_REST_API_KEY:
        log.error("❌ Thiếu OneSignal credentials!")
        log.error("Cần set:")
        log.error("  - ONESIGNAL_APP_ID")
        log.error("  - ONESIGNAL_REST_API_KEY")
        log.error("")
        log.error("Ví dụ:")
        log.error("  export ONESIGNAL_APP_ID='12345678-1234-1234-1234-123456789012'")
        log.error("  export ONESIGNAL_REST_API_KEY='NGFhNjJkYmItZjM5Yi00MjMwLWEwNDUtYjJhZDYzYzQ1NzUy'")
        return False
    
    log.info("App ID: %s", ONESIGNAL_APP_ID[:8] + "...")
    log.info("REST API Key: %s", ONESIGNAL_REST_API_KEY[:10] + "...")
    log.info("")
    
    # Dữ liệu test
    today = date.today().strftime("%d/%m/%Y")
    message = f"""Giá nông sản hôm nay ({today}) có sự biến động như sau:
Đắk Lắk 96,000 +1,200
Lâm Đồng 95,500 +1,300
Gia Lai 96,000 +1,200
Đắk Nông 96,000 +1,000
Hồ tiêu 146,000 +2,000"""
    
    # Payload OneSignal
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "included_segments": ["All"],
        "headings": {"en": "🌾 Giá Nông Sản Mới"},
        "contents": {"en": message},
        "url": "https://agriht.com/gia-nong-san/",
        "data": {
            "type": "price_update_test",
            "test": True
        }
    }
    
    try:
        log.info("📢 Đang gửi thông báo test...")
        # OneSignal uses direct REST API Key with Basic prefix
        response = requests.post(
            ONESIGNAL_URL,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Basic {ONESIGNAL_REST_API_KEY}"
            },
            timeout=15
        )
        
        log.info("HTTP Status: %d", response.status_code)
        
        if response.status_code == 200:
            result = response.json()
            recipients = result.get("recipients", 0)
            notification_id = result.get("id", "unknown")
            
            log.info("")
            log.info("=" * 60)
            log.info("✅ THÀNH CÔNG!")
            log.info("=" * 60)
            log.info("Notification ID: %s", notification_id)
            log.info("Recipients: %d thiết bị", recipients)
            log.info("")
            log.info("Thông báo đã được gửi!")
            log.info("Kiểm tra thiết bị mobile/browser đã subscribe.")
            log.info("")
            
            if recipients == 0:
                log.warning("⚠️  Không có thiết bị nào nhận thông báo!")
                log.warning("Cần:")
                log.warning("  1. Thêm OneSignal SDK vào website")
                log.warning("  2. Subscribe từ browser/app")
                log.warning("  3. Xem hướng dẫn: ONESIGNAL_SETUP.md")
            
            return True
        else:
            log.error("")
            log.error("=" * 60)
            log.error("❌ LỖI ONESIGNAL")
            log.error("=" * 60)
            log.error("HTTP Status: %d", response.status_code)
            log.error("Response: %s", response.text[:500])
            log.error("")
            log.error("Kiểm tra:")
            log.error("  - ONESIGNAL_APP_ID đúng?")
            log.error("  - ONESIGNAL_REST_API_KEY đúng?")
            log.error("  - Xem OneSignal Dashboard: https://app.onesignal.com/")
            return False
            
    except Exception as e:
        log.error("")
        log.error("=" * 60)
        log.error("❌ LỖI KẾT NỐI")
        log.error("=" * 60)
        log.error("Error: %s", e)
        log.error("")
        log.error("Kiểm tra kết nối internet")
        return False

if __name__ == "__main__":
    import sys
    success = test_onesignal()
    sys.exit(0 if success else 1)
