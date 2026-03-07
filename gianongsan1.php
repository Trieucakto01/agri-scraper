<?php
/**
 * gianongsan1.php
 * API endpoint nhan du lieu gia nong san tu GitHub Actions.
 */

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, X-Secret-Key');
header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Method not allowed']);
    exit();
}

define('SECRET_KEY', 'ditmecuocdoi');
define('DB_HOST', '153.92.15.31');
define('DB_USER', 'u697673786_Agriht');
define('DB_PASS', 'YOUR_PASSWORD_HERE');
define('DB_NAME', 'u697673786_Agriht');
define('DB_CHARSET', 'utf8mb4');

$headers = function_exists('getallheaders') ? getallheaders() : [];
$providedKey = $headers['X-Secret-Key'] ?? '';
if ($providedKey !== SECRET_KEY) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit();
}

$input = file_get_contents('php://input');
$data = json_decode($input, true);
if (!$data || !is_array($data)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Invalid JSON data']);
    exit();
}

try {
    $dsn = 'mysql:host=' . DB_HOST . ';dbname=' . DB_NAME . ';charset=' . DB_CHARSET;
    $pdo = new PDO($dsn, DB_USER, DB_PASS, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    ]);

    $pdo->exec("CREATE TABLE IF NOT EXISTS gia_nong_san (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ngay_cap_nhat DATE NOT NULL,
        san_pham VARCHAR(50) NOT NULL,
        thi_truong VARCHAR(100) NOT NULL,
        gia_trung_binh DECIMAL(15,2) DEFAULT 0,
        thay_doi DECIMAL(10,2) DEFAULT 0,
        ty_gia_usd_vnd DECIMAL(15,2) DEFAULT 0,
        cap_nhat_luc TIME,
        UNIQUE KEY uq_ngay_sp_tt (ngay_cap_nhat, san_pham, thi_truong)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");

    $sql = "INSERT INTO gia_nong_san (
                ngay_cap_nhat,
                san_pham,
                thi_truong,
                gia_trung_binh,
                thay_doi,
                ty_gia_usd_vnd,
                cap_nhat_luc
            ) VALUES (
                :ngay_cap_nhat,
                :san_pham,
                :thi_truong,
                :gia_trung_binh,
                :thay_doi,
                :ty_gia_usd_vnd,
                CURTIME()
            )
            ON DUPLICATE KEY UPDATE
                gia_trung_binh = VALUES(gia_trung_binh),
                thay_doi = VALUES(thay_doi),
                ty_gia_usd_vnd = VALUES(ty_gia_usd_vnd),
                cap_nhat_luc = CURTIME()";

    $stmt = $pdo->prepare($sql);

    $inserted = 0;
    $updated = 0;
    $errors = [];

    foreach ($data as $record) {
        $ngay_cap_nhat = $record['ngay_cap_nhat'] ?? null;
        $san_pham = $record['san_pham'] ?? null;
        $thi_truong = $record['thi_truong'] ?? null;
        $gia_trung_binh = (float)($record['gia_trung_binh'] ?? 0);
        $thay_doi = (float)($record['thay_doi'] ?? 0);
        $ty_gia_usd_vnd = (float)($record['ty_gia_usd_vnd'] ?? 0);

        if (!$ngay_cap_nhat || !$san_pham || !$thi_truong) {
            $errors[] = 'Missing required fields: ' . json_encode($record, JSON_UNESCAPED_UNICODE);
            continue;
        }

        // Gan gia tri
        $stmt->bindParam(':ngay_cap_nhat', $ngay_cap_nhat);
        $stmt->bindParam(':san_pham', $san_pham);
        $stmt->bindParam(':thi_truong', $thi_truong);
        $stmt->bindParam(':gia_trung_binh', $gia_trung_binh);
        $stmt->bindParam(':thay_doi', $thay_doi);
        $stmt->bindParam(':ty_gia_usd_vnd', $ty_gia_usd_vnd);

        $stmt->execute();

        if ($stmt->rowCount() === 1) {
            $inserted++;
        } elseif ($stmt->rowCount() >= 2) {
            $updated++;
        }
    }

    echo json_encode([
        'success' => true,
        'inserted' => $inserted,
        'updated' => $updated,
        'errors' => $errors,
    ], JSON_UNESCAPED_UNICODE);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage(),
    ], JSON_UNESCAPED_UNICODE);
}
