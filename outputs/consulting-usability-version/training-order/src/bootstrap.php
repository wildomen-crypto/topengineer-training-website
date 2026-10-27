<?php
declare(strict_types=1);

function settings(): array {
    static $settings;
    if (isset($settings)) return $settings;
    $path = getenv('TRAINING_ORDER_CONFIG');
    $settings = require ($path && is_file($path) ? $path : dirname(__DIR__).'/settings.example.php');
    if (!is_array($settings)) throw new RuntimeException('Invalid checkout settings.');
    return $settings;
}

function storage(): string {
    static $path;
    if (isset($path)) return $path;
    $candidate = getenv('TRAINING_ORDER_DATA_DIR');
    if (!$candidate) {
        if ((settings()['mode'] ?? '') === 'live') throw new RuntimeException('Private order storage must be configured.');
        $candidate = (getenv('LOCALAPPDATA') ?: sys_get_temp_dir()).'/TopEngineer/training-order-preview';
    }
    if (!is_dir($candidate) && !mkdir($candidate, 0700, true) && !is_dir($candidate)) throw new RuntimeException('Cannot initialise private storage.');
    $path = realpath($candidate);
    $root = realpath(dirname(__DIR__, 2));
    $normalise = fn($s) => strtolower(str_replace('\\', '/', $s));
    if (!$path || str_starts_with($normalise($path).'/', $normalise($root).'/')) throw new RuntimeException('Order storage must be outside the public site.');
    foreach (['sessions', 'pdf-cache'] as $folder) if (!is_dir($path.'/'.$folder)) mkdir($path.'/'.$folder, 0700, true);
    return $path;
}

function database(): PDO {
    static $db;
    if (isset($db)) return $db;
    $db = new PDO('sqlite:'.storage().'/orders.sqlite', null, null, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
    $db->exec('PRAGMA busy_timeout=8000');
    $db->exec('PRAGMA journal_mode=WAL');
    $db->exec('CREATE TABLE IF NOT EXISTS counters (series TEXT PRIMARY KEY, value INTEGER NOT NULL)');
    $db->exec('CREATE TABLE IF NOT EXISTS orders (
        token TEXT PRIMARY KEY, request_scope TEXT NOT NULL, request_key TEXT NOT NULL,
        body_hash TEXT NOT NULL, reference TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL,
        snapshot TEXT NOT NULL, UNIQUE(request_scope, request_key))');
    $db->exec('CREATE TABLE IF NOT EXISTS request_limits (bucket TEXT PRIMARY KEY, count INTEGER NOT NULL)');
    return $db;
}

function checkout_session(): array {
    session_save_path(storage().'/sessions');
    ini_set('session.use_strict_mode','1');
    ini_set('session.use_only_cookies','1');
    session_name('TE_TRAINING_ORDER');
    $cookiePath=rtrim(str_replace('\\','/',dirname($_SERVER['SCRIPT_NAME']??'/training-order/api.php')),'/').'/';
    session_set_cookie_params(['lifetime' => 0, 'path' => $cookiePath, 'secure' => !empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off', 'httponly' => true, 'samesite' => 'Strict']);
    session_start();
    $_SESSION['csrf'] ??= bin2hex(random_bytes(24));
    $_SESSION['scope'] ??= bin2hex(random_bytes(24));
    $data = ['csrf' => $_SESSION['csrf'], 'scope' => $_SESSION['scope']];
    session_write_close();
    return $data;
}

function limit_requests(string $kind): void {
    $limit = match($kind) { 'order'=>60, 'document'=>120, default=>600 };
    $bucket = hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? 'local').'|'.$kind.'|'.gmdate('Y-m-d-H'));
    $db = database();
    $db->prepare('INSERT INTO request_limits(bucket,count) VALUES(?,1) ON CONFLICT(bucket) DO UPDATE SET count=count+1')->execute([$bucket]);
    $statement = $db->prepare('SELECT count FROM request_limits WHERE bucket=?');
    $statement->execute([$bucket]);
    if ((int)$statement->fetchColumn() > $limit) throw new DomainException('Too many requests. Please try again later.', 429);
}

function json_reply(array $data, int $status = 200): never {
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR);
    exit;
}

function request_json(array $session): array {
    if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') throw new DomainException('Use POST for this action.', 405);
    if ((int)($_SERVER['CONTENT_LENGTH'] ?? 0) > 32768) throw new DomainException('The request is too large.', 413);
    if (!str_starts_with(strtolower($_SERVER['CONTENT_TYPE'] ?? ''), 'application/json')) throw new DomainException('Send a JSON request.', 415);
    if (!hash_equals($session['csrf'], $_SERVER['HTTP_X_CSRF_TOKEN'] ?? '')) throw new DomainException('Please reload the order page and try again.', 403);
    $origin = $_SERVER['HTTP_ORIGIN'] ?? '';
    if ($origin && !in_array($origin, settings()['allowed_origins'], true)) throw new DomainException('This origin is not allowed.', 403);
    $raw = file_get_contents('php://input', false, null, 0, 32769);
    if (strlen($raw) > 32768) throw new DomainException('The request is too large.', 413);
    try { $body = json_decode($raw, true, 24, JSON_THROW_ON_ERROR); }
    catch (JsonException) { throw new DomainException('The order could not be read. Please try again.', 422); }
    if (!is_array($body)) throw new DomainException('Invalid order.', 422);
    return $body;
}

function clean_text(mixed $value, string $label, int $limit = 200, bool $required = true): string {
    if (!is_string($value)) $value = '';
    $value = trim(preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', $value) ?? '');
    if (($required && $value === '') || mb_strlen($value) > $limit) throw new DomainException('Check '.$label.'.', 422);
    return $value;
}

function catalogue(): array {
    static $data;
    return $data ??= json_decode(file_get_contents(dirname(__DIR__).'/data/catalogue.json'), true, 64, JSON_THROW_ON_ERROR);
}
