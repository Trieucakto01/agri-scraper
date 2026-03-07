#!/usr/bin/env python3
"""
update_gianongsan.py
Script chính để scrape và cập nhật giá nông sản vào gianongsan1.php
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import sys
import logging
from scrape_giacaphe import chup_bang_gia, ocr_bang_gia, post_records

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

def main():
    """
    Chạy workflow chính:
    1. Scrape dữ liệu từ giacaphe.com
    2. OCR và parse dữ liệu
    3. POST tới PHP API endpoint
    """
    log.info("=" * 60)
    log.info("BẮT ĐẦU CẬP NHẬT GIÁ NÔNG SẢN")
    log.info("=" * 60)
    
    try:
        # Bước 1: Chụp bảng giá
        log.info("\n[1/3] Đang chụp bảng giá từ giacaphe.com...")
        img_bytes = chup_bang_gia()
        
        # Bước 2: OCR và parse
        log.info("\n[2/3] Đang OCR và parse dữ liệu...")
        records = ocr_bang_gia(img_bytes)
        
        if not records:
            log.error("❌ Không scrape được dữ liệu nào!")
            return 1
        
        log.info("✅ Đã parse được %d bản ghi", len(records))
        
        # Bước 3: POST tới database
        log.info("\n[3/3] Đang lưu dữ liệu...")
        post_records(records)
        
        log.info("\n" + "=" * 60)
        log.info("✅ HOÀN THÀNH CẬP NHẬT")
        log.info("=" * 60)
        return 0
        
    except KeyboardInterrupt:
        log.warning("\n⚠️  Bị ngắt bởi người dùng")
        return 130
    except Exception as e:
        log.error("\n❌ Lỗi: %s", e, exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
