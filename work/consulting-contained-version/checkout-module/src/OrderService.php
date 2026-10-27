<?php
declare(strict_types=1);

function commercial_terms(): array {
    $terms=settings()['commercial_terms'];
    if(!is_int($terms['validity_months']) || $terms['validity_months']<1 || $terms['validity_months']>60) throw new RuntimeException('Invalid invoice validity period.');
    return $terms;
}

function invoice_valid_until(DateTimeImmutable $issued, int $months): string {
    // Keep calendar months; 31 August + six months ends on the last day of February.
    $target=$issued->modify('first day of this month')->modify('+'.$months.' months');
    $day=min((int)$issued->format('j'),(int)$target->format('t'));
    return $target->setDate((int)$target->format('Y'),(int)$target->format('n'),$day)->format('Y-m-d');
}

function order_is_expired(array $order, ?DateTimeImmutable $today=null): bool {
    $until=$order['validUntil']??'';
    return $until!=='' && ($today??new DateTimeImmutable('now',new DateTimeZone('Europe/Belgrade')))->format('Y-m-d')>$until;
}

function bank_ready(array $config): bool {
    $bank = $config['bank'];
    $iban = strtoupper(preg_replace('/\s+/', '', $bank['iban'] ?? ''));
    if (!$bank['details_confirmed'] || !preg_match('/^[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}$/', $iban)) return false;
    $number = substr($iban,4).substr($iban,0,4);
    $remainder = 0;
    foreach (str_split($number) as $c) foreach (str_split(ctype_alpha($c) ? (string)(ord($c)-55) : $c) as $digit) $remainder = ($remainder*10+(int)$digit)%97;
    return $remainder === 1 && preg_match('/^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$/', strtoupper($bank['swift'] ?? '')) && !empty($bank['name']) && !empty($bank['beneficiary']) && ($bank['currency'] ?? '') === 'EUR';
}

function tax_rule(string $country, string $category='training'): array {
    $config = settings();
    $rules = $category==='books' ? ($config['book_tax_rules']??[]) : $config['tax_rules'];
    $rule = $rules[$country] ?? ($country !== 'RS' ? ($rules['foreign_business'] ?? []) : []);
    $mode = $rule['mode'] ?? 'unconfigured';
    $rate = $rule['rate_bps'] ?? 0;
    $ready = !empty($rule['approved']) && in_array($mode,['outside_scope','exempt','exclusive','inclusive'],true) && is_int($rate) && $rate >= 0 && $rate <= 10000 && !empty($rule['note']);
    return ['approved' => $ready, 'mode' => $ready ? $mode : 'unconfigured', 'rate_bps' => $ready ? $rate : 0, 'note' => $ready ? $rule['note'] : ($category==='books' ? 'Tax treatment for electronic books has not yet been confirmed. Book prices are indicative.' : 'Tax treatment has not yet been confirmed. This is an indicative training price.')];
}

function tax_amounts(int $price, array $tax): array {
    $basis = $tax['rate_bps'];
    if ($tax['mode'] === 'exclusive') {
        $vat = intdiv($price*$basis+5000,10000);
        return ['netCents'=>$price,'taxCents'=>$vat,'totalCents'=>$price+$vat];
    }
    if ($tax['mode'] === 'inclusive') {
        $net = intdiv($price*10000+intdiv(10000+$basis,2),10000+$basis);
        return ['netCents'=>$net,'taxCents'=>$price-$net,'totalCents'=>$price];
    }
    return ['netCents'=>$price,'taxCents'=>0,'totalCents'=>$price];
}

function make_quote(array $input, string $country = ''): array {
    $catalogue = catalogue();
    $rates = $catalogue['rates'];
    $product = $catalogue['bookProduct'];
    $bookQuantity = $input['bookQuantity']??0;
    if(!is_int($bookQuantity)||$bookQuantity<0||$bookQuantity>$product['maxQuantity']) throw new DomainException('Choose between 1 and '.$product['maxQuantity'].' book sets, or remove the books.',422);
    $source = $input['courses'] ?? null;
    if (!is_array($source) || !array_is_list($source) || count($source)>4 || (count($source)===0 && $bookQuantity===0)) throw new DomainException('Select a course or an electronic book set.',422);
    if ($country !== '' && !isset($catalogue['countries'][$country])) throw new DomainException('Select a valid company country.',422);
    $trainingTax = tax_rule($country);
    $tax = $trainingTax;
    $items=[]; $seen=[]; $subtotal=0; $net=0; $vat=0; $total=0;
    foreach ($source as $line) {
        if (!is_array($line)) throw new DomainException('Invalid course selection.',422);
        $level=$line['id']??null; $days=$line['days']??null; $participants=$line['participants']??null;
        if (!is_int($level)||$level<1||$level>4||isset($seen[$level])||!is_int($days)||!in_array($days,[2,5,10],true)||!is_int($participants)||$participants<1||$participants>20) throw new DomainException('Check course, duration and group size.',422);
        $seen[$level]=true;
        $billed=max($participants,$rates['minimumBillableParticipants'][(string)$days]);
        $price=$rates['totalsCents'][(string)$days][(string)$billed];
        $start=$line['startDate']??'';
        if (!is_string($start)) throw new DomainException('Check the desired start date.',422);
        $end='';
        if ($start!=='') {
            $date=DateTimeImmutable::createFromFormat('!Y-m-d',$start,new DateTimeZone('Europe/Belgrade'));
            if (!$date||$date->format('Y-m-d')!==$start||$start<'2000-01-01'||$start>'9999-12-01') throw new DomainException('Check the desired start date.',422);
            $end=$date->modify('+'.($days-1).' days')->format('Y-m-d');
        }
        $course=$catalogue['courses'][$level-1];
        $format=array_values(array_filter($catalogue['formats'],fn($f)=>$f['days']===$days))[0];
        $amounts=tax_amounts($price,$tax);
        $items[]=array_merge(['id'=>$level,'name'=>$course['title'],'days'=>$days,'hours'=>$days*8,'participants'=>$participants,'billedParticipants'=>$billed,'priceCents'=>$price,'startDate'=>$start,'endDate'=>$end,'format'=>$format['title']],$amounts);
        $subtotal+=$price; $net+=$amounts['netCents']; $vat+=$amounts['taxCents']; $total+=$amounts['totalCents'];
    }
    usort($items,fn($a,$b)=>$a['id']<=>$b['id']);
    $bookSet=null;
    if($bookQuantity>0) {
        $bookTax=tax_rule($country,'books');
        $price=$product['unitPriceCents']*$bookQuantity;
        $amounts=tax_amounts($price,$bookTax);
        $bookSet=array_merge(['id'=>$product['id'],'name'=>$product['name'],'description'=>$product['description'],'quantity'=>$bookQuantity,'unitPriceCents'=>$product['unitPriceCents'],'priceCents'=>$price],$amounts);
        $subtotal+=$price; $net+=$amounts['netCents']; $vat+=$amounts['taxCents']; $total+=$amounts['totalCents'];
        $tax=$items ? ['approved'=>$trainingTax['approved']&&$bookTax['approved'],'mode'=>'mixed','rate_bps'=>0,'note'=>$trainingTax['note'].' '.$bookTax['note']] : $bookTax;
    }
    $config=settings();
    $ready=$config['mode']==='live'&&!empty($config['seller']['details_confirmed'])&&bank_ready($config)&&$country!==''&&$tax['approved']&&!empty($config['payment_terms_approved']);
    $comparisonGroup=$items ? max(array_column($items,'participants')) : 1;
    $other=[];
    foreach($catalogue['courses'] as $course) if(!isset($seen[$course['level']])) {
        $prices=[];
        foreach([2,5,10] as $days) {
            $bill=max($comparisonGroup,$rates['minimumBillableParticipants'][(string)$days]);
            $base=$rates['totalsCents'][(string)$days][(string)$bill];
            $prices[(string)$days]=tax_amounts($base,$trainingTax)['totalCents'];
        }
        $other[]=['id'=>$course['level'],'name'=>$course['title'],'prices'=>$prices];
    }
    $result=['currency'=>'EUR','courses'=>$items,'bookSet'=>$bookSet,'courseCount'=>count($items),'days'=>array_sum(array_column($items,'days')),'hours'=>array_sum(array_column($items,'hours')),'subtotalCents'=>$subtotal,'netCents'=>$net,'taxCents'=>$vat,'totalCents'=>$total,'tax'=>$tax,'paymentReady'=>$ready,'comparisonParticipants'=>$comparisonGroup,'otherCourses'=>$other,'needsPrerequisiteConfirmation'=>count($items)>0&&!isset($seen[1]),'country'=>$country];
    $result['commercialTerms']=commercial_terms();
    $result['paymentTerm']=$config['payment_term'];
    $result['quoteFingerprint']=hash('sha256',json_encode([$result,$catalogue['revision']],JSON_UNESCAPED_UNICODE|JSON_THROW_ON_ERROR));
    return $result;
}

function customer_details(mixed $raw, bool $required): array {
    if (!is_array($raw)) throw new DomainException('Enter company billing details.',422);
    $customer=[];
    foreach(['companyName'=>[200,true],'registrationId'=>[100,true],'vatId'=>[100,false],'contactName'=>[160,true],'email'=>[254,true],'address'=>[700,true],'city'=>[160,true],'postalCode'=>[40,false],'country'=>[2,true],'phone'=>[80,false],'poReference'=>[120,false]] as $field=>$limits) $customer[$field]=clean_text($raw[$field]??'',$field,$limits[0],$required&&$limits[1]);
    $customer['country']=strtoupper($customer['country']);
    if($customer['email']!==''&&!filter_var($customer['email'],FILTER_VALIDATE_EMAIL)) throw new DomainException('Enter a valid email address.',422);
    if($customer['country']!==''&&!isset(catalogue()['countries'][$customer['country']])) throw new DomainException('Select a valid company country.',422);
    return $customer;
}

function proposal_snapshot(array $body): array {
    $customer=customer_details($body['customer']??[],false);
    $quote=make_quote($body,$customer['country']);
    $now=new DateTimeImmutable('now',new DateTimeZone('Europe/Belgrade'));
    // A quotation download is not an order and never consumes a pro forma number.
    $reference='TE-CP-'.$now->format('Ymd').'-'.strtoupper(substr(hash('sha256',json_encode([$quote['quoteFingerprint'],$customer],JSON_UNESCAPED_UNICODE|JSON_THROW_ON_ERROR)),0,8));
    return ['reference'=>$reference,'createdAt'=>$now->format(DATE_ATOM),'date'=>$now->format('Y-m-d'),'validUntil'=>null,'preview'=>!$quote['tax']['approved'],'customer'=>$customer,'quote'=>$quote,'seller'=>settings()['seller'],'bank'=>null,'commercialTerms'=>commercial_terms(),'catalogue'=>catalogue()];
}

function create_order(array $body, string $scope, string $key): array {
    if (!preg_match('/^[a-f0-9-]{24,80}$/i',$key)) throw new DomainException('Reload the page and try again.',422);
    $customer=customer_details($body['customer']??[],true);
    if(($body['businessAuthorised']??false)!==true) throw new DomainException('Confirm that you are authorised to order for this business.',422);
    $quote=make_quote($body,$customer['country']);
    if(!hash_equals($quote['quoteFingerprint'],(string)($body['quoteFingerprint']??''))) throw new DomainException('The price or tax details have changed. Review the updated total and prepare your documents again.',409);
    if($quote['needsPrerequisiteConfirmation']&&($body['prerequisiteConfirmed']??false)!==true) throw new DomainException('Confirm that participants have completed Level 1.',422);
    $includeAgreement=($body['includeAgreement']??false)===true;
    if($includeAgreement && $quote['courseCount']===0) throw new DomainException('A training agreement requires at least one training course.',422);
    $payload=['customer'=>$customer,'courses'=>$quote['courses'],'bookSet'=>$quote['bookSet'],'includeAgreement'=>$includeAgreement,'businessAuthorised'=>true,'prerequisiteConfirmed'=>($body['prerequisiteConfirmed']??false)===true];
    $hash=hash('sha256',json_encode($payload,JSON_UNESCAPED_UNICODE|JSON_THROW_ON_ERROR));
    $db=database();
    $db->exec('BEGIN IMMEDIATE');
    try {
        $find=$db->prepare('SELECT body_hash,snapshot FROM orders WHERE request_scope=? AND request_key=?');
        $find->execute([$scope,$key]);
        if($existing=$find->fetch(PDO::FETCH_ASSOC)) {
            if(!hash_equals($existing['body_hash'],$hash)) throw new DomainException('This request was already used for a different order. Please review your order and try again.',409);
            $db->exec('COMMIT');
            return json_decode($existing['snapshot'],true,64,JSON_THROW_ON_ERROR);
        }
        $now=new DateTimeImmutable('now',new DateTimeZone('Europe/Belgrade'));
        $series=($quote['paymentReady']?'TE-PF-':'PREVIEW-PF-').$now->format('Y');
        $counter=$db->prepare('INSERT INTO counters(series,value) VALUES(?,1) ON CONFLICT(series) DO UPDATE SET value=value+1');
        $counter->execute([$series]);
        $get=$db->prepare('SELECT value FROM counters WHERE series=?'); $get->execute([$series]);
        $reference=$series.'-'.str_pad((string)$get->fetchColumn(),6,'0',STR_PAD_LEFT);
        $config=settings();
        $snapshot=['token'=>bin2hex(random_bytes(32)),'reference'=>$reference,'createdAt'=>$now->format(DATE_ATOM),'date'=>$now->format('Y-m-d'),'preview'=>!$quote['paymentReady'],'status'=>$quote['paymentReady']?'awaiting_bank_transfer':'preview','customer'=>$customer,'quote'=>$quote,'seller'=>$config['seller'],'bank'=>$quote['paymentReady']?$config['bank']:null,'paymentTerm'=>$config['payment_term'],'agreementApproved'=>!empty($config['agreement_approved']),'agreementVersion'=>$config['agreement_version'],'includeAgreement'=>$includeAgreement,'catalogue'=>catalogue()];
        $snapshot['commercialTerms']=$quote['commercialTerms'];
        $snapshot['validUntil']=invoice_valid_until($now,$quote['commercialTerms']['validity_months']);
        $insert=$db->prepare('INSERT INTO orders(token,request_scope,request_key,body_hash,reference,created_at,snapshot) VALUES(?,?,?,?,?,?,?)');
        $insert->execute([$snapshot['token'],$scope,$key,$hash,$reference,$snapshot['createdAt'],json_encode($snapshot,JSON_UNESCAPED_UNICODE|JSON_THROW_ON_ERROR)]);
        $db->exec('COMMIT');
        return $snapshot;
    } catch(Throwable $error) { if($db->inTransaction()) $db->exec('ROLLBACK'); else {try{$db->exec('ROLLBACK');}catch(Throwable){}} throw $error; }
}

function get_order(string $token): array {
    if(!preg_match('/^[a-f0-9]{64}$/',$token)) throw new DomainException('Order not found.',404);
    $find=database()->prepare('SELECT snapshot FROM orders WHERE token=?');
    $find->execute([$token]); $data=$find->fetchColumn();
    if(!$data) throw new DomainException('Order not found.',404);
    return json_decode($data,true,64,JSON_THROW_ON_ERROR);
}

function public_order(array $order): array {
    $documents=[['kind'=>'summary','label'=>'Commercial proposal (1 page)','filename'=>$order['reference'].'-summary.pdf'],['kind'=>'proposal','label'=>'Detailed proposal & all course programmes','filename'=>$order['reference'].'-proposal.pdf'],['kind'=>'invoice','label'=>$order['preview']?'Pro forma invoice preview':'Pro forma invoice','filename'=>$order['reference'].'-proforma.pdf']];
    if($order['includeAgreement']) $documents[]=['kind'=>'agreement','label'=>$order['agreementApproved']?'Training agreement':'Draft training agreement','filename'=>$order['reference'].'-agreement.pdf'];
    $expired=order_is_expired($order);
    return ['token'=>$order['token'],'reference'=>$order['reference'],'date'=>$order['date'],'validUntil'=>$order['validUntil']??null,'expired'=>$expired,'commercialTerms'=>$order['commercialTerms']??null,'preview'=>$order['preview'],'status'=>$expired?'expired':$order['status'],'customer'=>$order['customer'],'quote'=>$order['quote'],'seller'=>$order['seller'],'bank'=>$expired?null:$order['bank'],'paymentTerm'=>$order['paymentTerm'],'agreementApproved'=>$order['agreementApproved'],'documents'=>$documents];
}
