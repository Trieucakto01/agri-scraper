import requests
from datetime import date, datetime

PHP_ENDPOINT = "https://agriht.com/gianongsan1.php"
SECRET_KEY = "ditmecuocdoi"

today = date.today().isoformat()
now = datetime.now().strftime("%H:%M:%S")

sample_data = [
    {
        "ngay_cap_nhat": today,
        "san_pham": "Cà phê",
        "thi_truong": "Đắk Lắk",
        "gia_trung_binh": 96000.0,
        "thay_doi": 1200.0,
        "ty_gia_usd_vnd": 25300.0,
        "cap_nhat_luc": now
    }
]

print(f"Sending POST to: {PHP_ENDPOINT}")
print(f"Data: {sample_data}")
print()

response = requests.post(
    PHP_ENDPOINT,
    json=sample_data,
    headers={
        "Content-Type": "application/json",
        "X-Secret-Key": SECRET_KEY
    },
    timeout=30
)

print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
print(f"Content-Length: {len(response.text)}")
print()
print(f"Raw Response (first 500 chars):")
print(repr(response.text[:500]))
print()
print(f"Hex dump (first 100 bytes):")
print(response.content[:100].hex())
