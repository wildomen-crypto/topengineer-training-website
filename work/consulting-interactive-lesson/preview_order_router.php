<?php
declare(strict_types=1);
$path=rawurldecode(parse_url($_SERVER['REQUEST_URI'],PHP_URL_PATH) ?: '/');
if(preg_match('~(?:^|/)\.[^/]*|^/training-order/(?:src|vendor|data)/|^/training-order/(?:settings\.example\.php|agreement-clauses\.json)~',$path)) {
    http_response_code(404);echo 'Not found';return true;
}
return false;
