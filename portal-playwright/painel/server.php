<?php

/**
 * Router do php -S (substitui o do Laravel).
 * O file_put_contents em php://stdout gera Notice "Broken pipe" no Docker
 * quando o pipe de log enche/fecha — e o Laravel transforma isso em 500.
 */

$publicPath = getcwd();

$uri = urldecode(
    parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) ?? ''
);

if ($uri !== '/' && file_exists($publicPath.$uri)) {
    return false;
}

$formattedDateTime = date('D M j H:i:s Y');
$requestMethod = $_SERVER['REQUEST_METHOD'] ?? 'GET';
$remoteAddress = ($_SERVER['REMOTE_ADDR'] ?? '-').':'.($_SERVER['REMOTE_PORT'] ?? '-');

@file_put_contents('php://stdout', "[$formattedDateTime] $remoteAddress [$requestMethod] URI: $uri\n");

require_once $publicPath.'/index.php';
