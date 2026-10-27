<?php
declare(strict_types=1);
require __DIR__.'/src/bootstrap.php';
require __DIR__.'/src/OrderService.php';
require __DIR__.'/src/Documents.php';
header('Cache-Control: no-store, private');
header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: no-referrer');
try {
    $action=$_GET['action']??'config';
    if($action==='course-programme') {
        if(($_SERVER['REQUEST_METHOD']??'GET')!=='GET') throw new DomainException('Method not allowed.',405);
        $level=$_GET['level']??'';
        if(!is_string($level)||!preg_match('/^[1-4]$/',$level)) throw new DomainException('Course not found.',404);
        limit_requests('document');
        $courses=catalogue()['courses']; $course=null;
        foreach($courses as $item) if($item['level']===(int)$level) { $course=$item; break; }
        if(!$course) throw new DomainException('Course not found.',404);
        $content=render_course_programme_pdf($course);
        header('Content-Type: application/pdf');
        header('Content-Disposition: attachment; filename="TopEngineer-Level-'.$level.'-programme.pdf"');
        header('Content-Length: '.strlen($content)); echo $content; exit;
    }
    if(in_array($action,['config','quote','proposal','order','resume'],true)) $session=checkout_session();
    if($action==='config') {
        if(($_SERVER['REQUEST_METHOD']??'GET')!=='GET') throw new DomainException('Method not allowed.',405);
        $config=settings();
        $find=database()->prepare('SELECT reference FROM orders WHERE request_scope=? LIMIT 1');$find->execute([$session['scope']]);
        json_reply(['csrf'=>$session['csrf'],'mode'=>$config['mode'],'seller'=>$config['seller'],'agreementApproved'=>$config['agreement_approved'],'countries'=>catalogue()['countries'],'bankConfigured'=>bank_ready($config),'resumeAvailable'=>(bool)$find->fetchColumn()]);
    }
    if($action==='resume') {
        if(($_SERVER['REQUEST_METHOD']??'GET')!=='GET') throw new DomainException('Method not allowed.',405);
        $find=database()->prepare('SELECT snapshot FROM orders WHERE request_scope=? ORDER BY created_at DESC, rowid DESC LIMIT 1');$find->execute([$session['scope']]);$snapshot=$find->fetchColumn();
        if(!$snapshot) throw new DomainException('No order is available in this browser session.',404);
        json_reply(public_order(json_decode($snapshot,true,64,JSON_THROW_ON_ERROR)));
    }
    if($action==='quote') {
        $body=request_json($session);limit_requests('quote');
        $country=clean_text($body['country']??'','country',2,false);
        json_reply(make_quote($body,strtoupper($country)));
    }
    if($action==='order') {
        $body=request_json($session);limit_requests('order');
        $key=$_SERVER['HTTP_IDEMPOTENCY_KEY']??'';
        $order=create_order($body,$session['scope'],$key);
        json_reply(public_order($order),201);
    }
    if($action==='proposal') {
        $body=request_json($session);limit_requests('document');
        $proposal=proposal_snapshot($body);
        $content=render_pdf($proposal,'summary');
        header('Content-Type: application/pdf');
        header('Content-Disposition: attachment; filename="'.$proposal['reference'].'-proposal.pdf"');
        header('Content-Length: '.strlen($content));echo $content;exit;
    }
    if($action==='document') {
        if(($_SERVER['REQUEST_METHOD']??'GET')!=='GET') throw new DomainException('Method not allowed.',405);
        $auth=$_SERVER['HTTP_AUTHORIZATION']??'';
        $order=get_order(str_starts_with($auth,'Bearer ')?substr($auth,7):'');
        limit_requests('document');
        $kind=$_GET['kind']??'';
        if(!in_array($kind,['summary','proposal','invoice','agreement','pack'],true)) throw new DomainException('Document not found.',404);
        $content=$kind==='pack'?render_pack($order):render_pdf($order,$kind);
        header('Content-Type: '.($kind==='pack'?'application/zip':'application/pdf'));
        header('Content-Disposition: attachment; filename="'.$order['reference'].'-'.$kind.($kind==='pack'?'.zip':'.pdf').'"');
        header('Content-Length: '.strlen($content));echo $content;exit;
    }
    throw new DomainException('Not found.',404);
} catch(DomainException $error) {
    $status=$error->getCode(); if($status<400||$status>499) $status=422;
    json_reply(['error'=>$error->getMessage()],$status);
} catch(Throwable $error) {
    error_log('TopEngineer checkout: '.get_class($error).': '.$error->getMessage());
    json_reply(['error'=>'The documents could not be prepared. Your selection is saved in this tab; please try again.'],500);
}
