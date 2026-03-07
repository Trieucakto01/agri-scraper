#!/usr/bin/env python3
"""
test_mysql.py
Kiểm tra kết nối MySQL và chèn dữ liệu test
"""

import os
import sys
import logging
import mysql.connector
from datetime import date, time
from decimal import Decimal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

# MySQL Configuration (Using Hostinger IP for better connectivity)
DB_CONFIG = {
    "host":     os.environ.get("DB_HOST", "srv1631.hstgr.io"),
    "port":     int(os.environ.get("DB_PORT") or "3306"),
    "database": os.environ.get("DB_NAME", "u697673786_Agriht"),
    "user":     os.environ.get("DB_USER", "u697673786_Agriht"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "charset":  "utf8mb4",
    "connection_timeout": int(os.environ.get("DB_TIMEOUT") or "12"),
    "autocommit": True,
}

def test_connection():
    """Test kết nối MySQL"""
    log.info("=" * 70)
    log.info("KIỂM TRA KẾT NỐI MYSQL")
    log.info("=" * 70)
    log.info("")
    log.info("Config:")
    log.info("  Host: %s", DB_CONFIG["host"])
    log.info("  Port: %s", DB_CONFIG["port"])
    log.info("  User: %s", DB_CONFIG["user"])
    log.info("  Database: %s", DB_CONFIG["database"])
    log.info("  Timeout: %ss", DB_CONFIG["connection_timeout"])
    log.info("")
    
    try:
        log.info("Đang kết nối...")
        conn = mysql.connector.connect(**DB_CONFIG)
        
        log.info("✅ Kết nối thành công!")
        log.info("")
        
        cursor = conn.cursor()
        
        # Check MySQL version
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        log.info("MySQL Version: %s", version)
        
        # Create table if not exists
        log.info("")
        log.info("Đang tạo table (nếu cần)...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gia_nong_san (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                ngay_cap_nhat   DATE          NOT NULL,
                san_pham        VARCHAR(50)   NOT NULL,
                thi_truong      VARCHAR(100)  NOT NULL,
                gia_trung_binh  DECIMAL(15,2) DEFAULT 0,
                thay_doi        DECIMAL(10,2) DEFAULT 0,
                ty_gia_usd_vnd  DECIMAL(15,2) DEFAULT 0,
                cap_nhat_luc    TIME,
                UNIQUE KEY uq_ngay_sp_tt (ngay_cap_nhat, san_pham, thi_truong)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        log.info("✅ Table sẵn sàng")
        
        # Insert test data
        log.info("")
        log.info("Đang chèn dữ liệu test...")
        
        test_data = [
            {
                'ngay_cap_nhat': date.today(),
                'san_pham': 'Cà phê',
                'thi_truong': 'Tây Nguyên',
                'gia_trung_binh': Decimal('32500.00'),
                'thay_doi': Decimal('500.00'),
                'ty_gia_usd_vnd': Decimal('24500.00'),
                'cap_nhat_luc': '14:30:00'
            },
            {
                'ngay_cap_nhat': date.today(),
                'san_pham': 'Tiêu',
                'thi_truong': 'TP.HCM',
                'gia_trung_binh': Decimal('95000.00'),
                'thay_doi': Decimal('-1000.00'),
                'ty_gia_usd_vnd': Decimal('24500.00'),
                'cap_nhat_luc': '14:30:00'
            }
        ]
        
        sql = """
            INSERT INTO gia_nong_san
            (ngay_cap_nhat, san_pham, thi_truong, gia_trung_binh, thay_doi, ty_gia_usd_vnd, cap_nhat_luc)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            gia_trung_binh = VALUES(gia_trung_binh),
            thay_doi = VALUES(thay_doi),
            ty_gia_usd_vnd = VALUES(ty_gia_usd_vnd),
            cap_nhat_luc = VALUES(cap_nhat_luc)
        """
        
        inserted = 0
        updated = 0
        
        for data in test_data:
            cursor.execute(sql, (
                data['ngay_cap_nhat'],
                data['san_pham'],
                data['thi_truong'],
                data['gia_trung_binh'],
                data['thay_doi'],
                data['ty_gia_usd_vnd'],
                data['cap_nhat_luc']
            ))
            
            if cursor.rowcount == 1:
                inserted += 1
            elif cursor.rowcount == 2:
                updated += 1
        
        conn.commit()
        log.info("✅ Chèn/cập nhật xong: %d inserted, %d updated", inserted, updated)
        
        # Show data
        log.info("")
        log.info("Dữ liệu hiện tại trong table:")
        cursor.execute("SELECT ngay_cap_nhat, san_pham, thi_truong, gia_trung_binh FROM gia_nong_san ORDER BY ngay_cap_nhat DESC LIMIT 5")
        for row in cursor.fetchall():
            log.info("  %s | %s | %s | GIA: %s", row[0], row[1], row[2], row[3])
        
        cursor.close()
        conn.close()
        
        log.info("")
        log.info("=" * 70)
        log.info("✅ TẤT CẢ TEST THÀNH CÔNG!")
        log.info("=" * 70)
        return 0
        
    except mysql.connector.Error as e:
        log.error("")
        log.error("=" * 70)
        log.error("❌ LỖI MYSQL")
        log.error("=" * 70)
        log.error("Error %d: %s", e.errno, e.msg)
        log.error("")
        log.error("TROUBLESHOOTING:")
        
        if e.errno == 2003:
            log.error("  - Không kết nối được host: %s", DB_CONFIG["host"])
            log.error("  - Kiểm tra: host có đúng không?")
            log.error("  - Cổng: %s", DB_CONFIG["port"])
            log.error("")
            log.error("  🔧 SOLUTION: Cần whitelist IP của GitHub Codespace ở Hostinger")
            log.error("")
            log.error("  Các bước:")
            log.error("    1. Vào Hostinger Control Panel")
            log.error("    2. Databases → MySQL → Remote MySQL")
            log.error("    3. Thêm Current Codespace IP: (you need to get this)")
            log.error("    4. Hoặc Add: 0.0.0.0/0 (allow all - tạm thời)")
            log.error("")
            log.error("  Lấy IP hiện tại:")
            log.error("    $ curl https://api.ipify.org")
        elif e.errno == 1045:
            log.error("  - Sai user hoặc password")
            log.error("  - DB_USER: %s", DB_CONFIG["user"])
            log.error("  - DB_HOST: %s", DB_CONFIG["host"])
        elif e.errno == 1049:
            log.error("  - Database không tồn tại: %s", DB_CONFIG["database"])
        
        return 1
    
    except Exception as e:
        log.error("")
        log.error("=" * 70)
        log.error("❌ LỖI: %s", e)
        log.error("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(test_connection())
