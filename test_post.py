#!/usr/bin/env python3
"""
test_post.py
Script test để POST dữ liệu mẫu vào gianongsan1.php
"""

import os
import requests
import logging
from datetime import date, datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# Cấu hình
PHP_ENDPOINT = os.environ.get("PHP_ENDPOINT", "https://agriht.com/gianongsan1.php")
SECRET_KEY   = os.environ.get("SECRET_KEY", "ditmecuocdoi")

def test_post_data():
    """
    Gửi dữ liệu mẫu để test endpoint PHP
    """
    today = date.today().isoformat()
    now   = datetime.now().strftime("%H:%M:%S")
    
    # Dữ liệu mẫu
    sample_data = [
        {
            "ngay_cap_nhat":  today,
            "san_pham":       "Cà phê",
            "thi_truong":     "Đắk Lắk",
            "gia_trung_binh": 96000.0,
            "thay_doi":       1200.0,
            "ty_gia_usd_vnd": 25300.0,
            "cap_nhat_luc":   now
        },
        {
            "ngay_cap_nhat":  today,
            "san_pham":       "Cà phê",
            "thi_truong":     "Gia Lai",
            "gia_trung_binh": 95500.0,
            "thay_doi":       800.0,
            "ty_gia_usd_vnd": 25300.0,
            "cap_nhat_luc":   now
        },
        {
            "ngay_cap_nhat":  today,
            "san_pham":       "Tiêu",
            "thi_truong":     "Đồng Nai",
            "gia_trung_binh": 145000.0,
            "thay_doi":       -500.0,
            "ty_gia_usd_vnd": 25300.0,
            "cap_nhat_luc":   now
        },
        {
            "ngay_cap_nhat":  today,
            "san_pham":       "Tiêu",
            "thi_truong":     "Bà Rịa - Vũng Tàu",
            "gia_trung_binh": 144500.0,
            "thay_doi":       0.0,
            "ty_gia_usd_vnd": 25300.0,
            "cap_nhat_luc":   now
        }
    ]
    
    log.info("=" * 60)
    log.info("TEST POST DỮ LIỆU VÀO ENDPOINT")
    log.info("=" * 60)
    log.info("Endpoint: %s", PHP_ENDPOINT)
    log.info("Số bản ghi: %d", len(sample_data))
    
    try:
        # Gửi POST request
        response = requests.post(
            PHP_ENDPOINT,
            json=sample_data,
            headers={
                "Content-Type": "application/json",
                "X-Secret-Key": SECRET_KEY
            },
            timeout=30
        )
        
        log.info("HTTP Status: %d", response.status_code)
        
        if response.status_code == 200:
            result = response.json()
            log.info("=" * 60)
            log.info("✅ THÀNH CÔNG")
            log.info("  - Inserted: %d", result.get("inserted", 0))
            log.info("  - Updated: %d", result.get("updated", 0))
            if result.get("errors"):
                log.warning("  - Errors: %s", result.get("errors"))
            log.info("=" * 60)
            return True
        else:
            log.error("❌ Lỗi HTTP %d", response.status_code)
            return False
            
    except Exception as e:
        log.error("❌ Lỗi: %s", e)
        return False

if __name__ == "__main__":
    import sys
    success = test_post_data()
    sys.exit(0 if success else 1)
