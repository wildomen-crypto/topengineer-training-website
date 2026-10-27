<?php
declare(strict_types=1);
require_once __DIR__.'/Proposal.php';

function e(string|int $text): string {
    return htmlspecialchars(str_replace(["\u{2011}","\u{2013}","\u{2014}"],'-',(string)$text),ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8');
}
function money(int $cents): string { return 'EUR '.number_format($cents/100,2,'.',','); }
function date_label(string $date): string { return $date ? (new DateTimeImmutable($date))->format('d M Y') : 'To be agreed'; }

function commercial_terms_html(array $order): string {
    $terms=$order['commercialTerms']??null;
    if(!$terms) return '';
    return '<p class="small"><strong>Invoice terms:</strong> Valid for '.e($terms['validity_months']).' calendar months from issue. '.e($terms['rescheduling']).' '.e($terms['refunds']).'</p>';
}

function document_start(array $order, string $title, bool $draft = false): string {
    $ref=e($order['reference']); $seller=e($order['seller']['legal_name']);
    $warning=$draft?'<div class="notice">DRAFT FOR REVIEW - not an executed agreement.</div>':($order['preview']?'<div class="notice">PREVIEW ONLY - NOT VALID FOR PAYMENT.</div>':'');
    $validityLabel=$title==='Training services agreement'?'Invoice valid until: ':'Valid until: ';
    $validity=empty($order['validUntil'])?'':' &nbsp; | &nbsp; <strong>'.$validityLabel.e(date_label($order['validUntil'])).'</strong>';
    return '<!doctype html><html><head><meta charset="utf-8"><style>
    @page { margin: 53pt 38pt 46pt; }
    body { font-family: "DejaVu Sans",sans-serif; font-size: 8.5pt; line-height: 1.3; color: #263746; }
    .running { position: fixed; top: -31pt; left: 0; right: 0; color: #054a85; border-bottom: 1pt solid #d3dee8; padding-bottom: 5pt; font-size: 8pt; }
    .running span { float: right; color: #667684; }
    .brand { color: #054a85; font-size: 14pt; font-weight: bold; letter-spacing: .7pt; }
    h1 { font-size: 25pt; line-height: 1.2; color: #054a85; margin: 4pt 0 8pt; }
    h2 { font-size: 15pt; color: #054a85; margin: 12pt 0 6pt; page-break-after: avoid; }
    h3 { font-size: 10pt; color: #054a85; margin: 8pt 0 4pt; page-break-after: avoid; }
    p { margin: 0 0 6pt; }
    .meta,.small { font-size: 8pt; color: #5f707f; }
    .notice { padding: 7pt; background: #fff3dc; border-left: 3pt solid #d99024; font-size: 8pt; margin: 6pt 0 9pt; }
    .note { padding: 8pt; background: #edf5fb; margin: 8pt 0; }
    table { border-collapse: collapse; width: 100%; margin: 5pt 0 8pt; table-layout: fixed; }
    th { background: #edf4fa; color: #054a85; text-align: left; font-size: 8pt; }
    td,th { padding: 4pt; border-bottom: .5pt solid #d4dfe8; vertical-align: top; word-wrap: break-word; }
    tr { page-break-inside: avoid; }
    thead { display: table-header-group; }
    .amount { text-align: right; white-space: nowrap; }
    .parties td { background: #f7f9fb; width: 50%; padding: 7pt; font-size: 8pt; }
    .totals { width: 56%; margin-left: 44%; }
    .totals .grand td { font-size: 12pt; font-weight: bold; background: #edf5fb; color: #054a85; }
    .new-page { page-break-before: always; }
    .topics { font-size: 8pt; line-height: 1.2; margin: 2pt 0 4pt; }
    .topics td { width: 50%; padding: 1pt 5pt; }
    .topic-entry { margin: 0 0 3pt; }
    .topic-code { color: #6c8090; }
    .programme-head { background: #edf5fb; padding: 8pt; margin-bottom: 8pt; }
    .programme h3 { font-size: 9.5pt; margin: 5pt 0 3pt; }
    .agreement { font-size: 8pt; line-height: 1.25; }
    .agreement h3 { margin: 6pt 0 3pt; }
    .agreement p { margin-bottom: 4pt; }
    .agreement td, .agreement th { padding: 3pt; }
    .clause { page-break-inside: avoid; }
    .invoice { font-size: 8pt; line-height: 1.22; }
    .invoice td,.invoice th { padding: 3pt; }
    .invoice table { margin: 3pt 0 6pt; }
    .invoice .totals td { padding: 2pt 3pt; }
    .invoice .totals { margin-left: 44%; }
    .invoice .parties td { font-size: 7.5pt; padding: 5pt; }
    .invoice p { margin-bottom: 3pt; }
    .invoice h2 { font-size: 13pt; margin: 8pt 0 5pt; }
    .bank-instructions { background: #edf5fb; padding: 7pt; font-size: 8pt; }
    .signatures td { height: 65pt; width: 50%; border: .5pt solid #d4dfe8; }
    </style></head><body><div class="running">TOPENGINEER <span>'.$ref.' | '.$seller.'</span></div>'.$warning.'<div class="brand">TOPENGINEER</div><h1>'.e($title).'</h1><p class="meta">Reference: '.$ref.' &nbsp; | &nbsp; Issued: '.e(date_label($order['date'])).' &nbsp; | &nbsp; Currency: EUR'.$validity.'</p>';
}

function parties_html(array $order): string {
    $s=$order['seller']; $b=$order['customer'];
    return '<table class="parties"><tr><td><strong>Supplier</strong><br>'.e($s['legal_name']).'<br>'.nl2br(e($s['address'])).'<br>Registration: '.e($s['registration_number']).'<br>Tax ID (PIB): '.e($s['tax_number']).(!empty($s['director'])?'<br>Director: '.e($s['director']):'').'<br>'.e($s['email']).'</td><td><strong>Customer</strong><br>'.e($b['companyName']).'<br>'.nl2br(e($b['address'])).'<br>'.e(trim($b['postalCode'].' '.$b['city'])).'<br>'.e($order['catalogue']['countries'][$b['country']]).'<br>Business ID: '.e($b['registrationId']).($b['vatId']?'<br>VAT / tax ID: '.e($b['vatId']):'').'<br>Contact: '.e($b['contactName']).'<br>'.e($b['email']).($b['poReference']?'<br>PO / reference: '.e($b['poReference']):'').'</td></tr></table>';
}

function order_table_html(array $order): string {
    $html='<table><thead><tr><th style="width:48%">Selected course</th><th style="width:17%">Duration</th><th style="width:13%">Group</th><th class="amount" style="width:22%">Group price</th></tr></thead><tbody>';
    foreach($order['quote']['courses'] as $course) {
        $schedule=$course['startDate']?date_label($course['startDate']).' to '.date_label($course['endDate']):'Dates to be agreed';
        $minimum=$course['billedParticipants']>$course['participants']?'<br><span class="small">Minimum fee for '.$course['billedParticipants'].'</span>':'';
        $html.='<tr><td><strong>Level '.$course['id'].' - '.e($course['name']).'</strong><br><span class="small">'.e($schedule).' (provisional)</span></td><td>'.$course['days'].' days<br>'.$course['hours'].' hours</td><td>'.$course['participants'].' attending'.$minimum.'</td><td class="amount">'.money($course['totalCents']).'</td></tr>';
    }
    $q=$order['quote'];
    $taxValue=$q['tax']['approved']?money($q['taxCents']):'Not confirmed';
    return $html.'</tbody></table><table class="totals"><tr><td>Training subtotal</td><td class="amount">'.money($q['netCents']).'</td></tr><tr><td>'.($q['tax']['approved']?'Tax / VAT':'Tax treatment').'</td><td class="amount">'.$taxValue.'</td></tr><tr class="grand"><td>'.($order['preview']?'Indicative total':'Amount payable').'</td><td class="amount">'.money($q['totalCents']).'</td></tr></table><p class="small">'.e($q['tax']['note']).'</p>';
}

function programme_html(array $course, string $context): string {
    $html='';
    foreach($course['days'] as $part) {
        $html.='<div class="new-page programme"><div class="programme-head"><p class="small">'.e($context).'</p><h2 style="margin:0">Level '.$course['level'].' - '.e($course['title']).'</h2><p class="small" style="margin:4pt 0 0">Two programme parts. Timing and practical work depend on the selected 2-, 5- or 10-day format.</p></div>';
        $html.='<h3>Part '.$part['day'].' - '.e($part['label']).'</h3>';
        foreach($part['sections'] as $section) {
            $html.='<h3>'.e($section['title']).'</h3>';
            if(!empty($section['note'])) $html.='<p class="small">'.e($section['note']).'</p>';
            $html.='<table class="topics"><tbody><tr>';
            $columns=array_chunk($section['topics'],(int)ceil(count($section['topics'])/2));
            foreach($columns as $topics) {
                $html.='<td>';
                foreach($topics as $topic) $html.='<div class="topic-entry"><span class="topic-code">'.e($topic[0]).'</span> &nbsp; '.e($topic[1]).'</div>';
                $html.='</td>';
            }
            if(count($columns)===1) $html.='<td></td>';
            $html.='</tr></tbody></table>';
        }
        $html.='</div>';
    }
    return $html;
}

function render_course_programme_pdf(array $course): string {
    require_once dirname(__DIR__).'/vendor/dompdf/autoload.inc.php';
    $html='<!doctype html><html><head><meta charset="utf-8"><style>
      @page { margin: 42pt 38pt 46pt; }
      body { font-family: "DejaVu Sans",sans-serif; font-size: 8.5pt; line-height: 1.3; color: #263746; }
      .programme { page-break-before: always; } .programme:first-child { page-break-before: auto; }
      .programme-head { background: #edf5fb; padding: 8pt; margin-bottom: 8pt; }
      h2 { font-size: 15pt; color: #054a85; margin: 0; } h3 { font-size: 9.5pt; color: #054a85; margin: 5pt 0 3pt; page-break-after: avoid; }
      p { margin: 0 0 6pt; } .small { font-size: 8pt; color: #5f707f; }
      table { width: 100%; table-layout: fixed; border-collapse: collapse; } tr { page-break-inside: avoid; }
      .topics { font-size: 8pt; line-height: 1.2; margin: 2pt 0 4pt; }
      .topics td { width: 50%; vertical-align: top; padding: 1pt 5pt; } .topic-entry { margin: 0 0 3pt; }
      .topic-code { color: #6c8090; }
    </style></head><body>'.programme_html($course,'TOPENGINEER - COURSE PROGRAMME').'</body></html>';
    $options=new \Dompdf\Options();
    $options->set('isRemoteEnabled',false); $options->set('isPhpEnabled',false); $options->set('isJavascriptEnabled',false);
    $options->set('chroot',dirname(__DIR__)); $options->set('tempDir',storage().'/pdf-cache'); $options->set('fontCache',storage().'/pdf-cache');
    $pdf=new \Dompdf\Dompdf($options); $pdf->setPaper('A4','portrait'); $pdf->loadHtml($html,'UTF-8'); $pdf->render();
    $font=$pdf->getFontMetrics()->getFont('DejaVu Sans','normal');
    $pdf->getCanvas()->page_text(38,817,'TopEngineer | Course programme',$font,7,[.35,.43,.49]);
    $pdf->getCanvas()->page_text(503,817,'{PAGE_NUM} / {PAGE_COUNT}',$font,7,[.35,.43,.49]);
    return $pdf->output();
}

function proposal_html(array $order): string {
    $q=$order['quote'];
    $html=document_start($order,'Commercial proposal').parties_html($order).'<h2>Your selected training</h2>'.order_table_html($order);
    $html.='<div class="note"><strong>Dates do not affect the training price.</strong> You can arrange payment before the teaching dates are finalised. Requested dates are provisional and are confirmed with your instructor. End dates include all calendar days, with the start date counted as day 1.</div>';
    $html.=commercial_terms_html($order);
    $selected=array_column($q['courses'],'id');
    foreach($order['catalogue']['courses'] as $course) if(in_array($course['level'],$selected,true)) $html.=programme_html($course,'SELECTED COURSE - included in the order total');
    $html.='<div class="new-page"><h2>Included in your training</h2><p>Live online instruction with a professional engineer, guided demonstrations and practical exercises appropriate to the chosen duration. The 10-day format includes five training days and five days on your own pilot project. Software preparation is arranged before the first lesson.</p><p>Each participant receives a personalised digital TopEngineer certificate with a unique number after completing the course. Brief follow-up questions can be answered free of charge; more involved technical support is agreed separately at an hourly rate.</p><p>Complete Level 1 before attending Levels 2-4. The advanced courses may be taken in any order.</p><p class="small">Software licences are not included. Bank transfer instructions appear in the separate pro forma invoice when payment is available.</p>';
    if($q['otherCourses']) {
        $html.='<h2>Other courses you can add</h2><p>These courses are <strong>not ordered and not included in your invoice</strong>. Prices below are for a group of '.$q['comparisonParticipants'].' participant'.($q['comparisonParticipants']===1?'':'s').' - the largest group size in your current plan.</p><table><thead><tr><th style="width:46%">Additional course</th><th class="amount" style="width:18%">2 days / 16 h</th><th class="amount" style="width:18%">5 days / 40 h</th><th class="amount" style="width:18%">10 days / 80 h</th></tr></thead><tbody>';
        foreach($q['otherCourses'] as $extra) $html.='<tr><td>Level '.$extra['id'].' - '.e($extra['name']).'</td><td class="amount">'.money($extra['prices']['2']).'</td><td class="amount">'.money($extra['prices']['5']).'</td><td class="amount">'.money($extra['prices']['10']).'</td></tr>';
        $html.='</tbody></table><p class="small">For 5- and 10-day formats, the minimum fee covers three participants even when one or two attend. Prices use the same tax treatment as this proposal. Additional courses are optional and are never charged automatically.</p><p>Browse and calculate another training plan at <a href="https://top-engineer.com/consulting/">top-engineer.com/consulting/</a>.</p></div>';
        foreach($order['catalogue']['courses'] as $course) if(!in_array($course['level'],$selected,true)) $html.=programme_html($course,'OPTIONAL ADDITIONAL COURSE - not included in the order total');
    } else $html.='</div>';
    return $html.'</body></html>';
}

function invoice_html(array $order): string {
    $html=document_start($order,'Pro forma invoice').'<div class="invoice"><p class="small">Payment request for live online Tekla Structures training. This document is not a tax invoice or proof of payment.</p>'.parties_html($order).order_table_html($order);
    if($order['bank']) {
        $bank=$order['bank'];
        $html.='<h2>Bank transfer instructions</h2><div class="bank-instructions">';
        foreach(['Beneficiary'=>$bank['beneficiary'],'IBAN'=>$bank['iban'],'SWIFT / BIC'=>$bank['swift'],'Bank'=>$bank['name'],'Bank address'=>$bank['address'],'Correspondent bank'=>$bank['correspondent'],'Payment reference'=>$order['reference'].' (EUR)'] as $label=>$value) if($value!=='') $html.='<p>'.e($label).': <strong>'.e($value).'</strong></p>';
        $html.='</div><p style="margin-top:6pt">'.e($order['paymentTerm']).'</p><p class="small">Please include the exact reference above. Payment remains pending until funds are received in the supplier bank account.</p>';
    } else $html.='<div class="notice"><strong>Not valid for payment.</strong> This preview contains no payment instructions. Required payment settings and the applicable tax treatment must be confirmed before a payable pro forma invoice can be issued.</div>';
    return $html.commercial_terms_html($order).'<p class="small">Training dates are provisional and agreed separately. Only selected courses are invoiced; optional courses are excluded.</p></div></body></html>';
}

function agreement_html(array $order): string {
    $html=document_start($order,'Training services agreement',!$order['agreementApproved']).'<div class="agreement">'.parties_html($order);
    $clauses=$order['catalogue']['agreementClauses'];
    foreach($clauses as $index=>$clause) $html.='<div class="clause"><h3>'.($index+1).'. '.e($clause['title']).'</h3><p>'.e($clause['text']).'</p></div>';
    $html.='<h2>Order schedule</h2>'.order_table_html($order).'<p>This agreement relates to proposal and pro forma reference <strong>'.e($order['reference']).'</strong>. The selected course programmes in that proposal form the training scope; optional additional courses are excluded.</p>';
    if(!$order['agreementApproved']) $html.='<div class="notice">Template version '.e($order['agreementVersion']).'. This draft requires review and agreement by both parties. No signature or acceptance has been recorded by the website.</div>';
    $signatory=!empty($order['seller']['director'])?e($order['seller']['director']).', Director':'';
    return $html.'<table class="signatures"><tr><td><strong>For the supplier</strong><br>Name / position: '.$signatory.'<br>Signature:<br>Date:</td><td><strong>For the customer</strong><br>Name / position:<br>Signature:<br>Date:</td></tr></table></div></body></html>';
}

function render_pdf(array $order, string $kind): string {
    require_once dirname(__DIR__).'/vendor/dompdf/autoload.inc.php';
    $html=match($kind) {'summary'=>summary_proposal_html($order),'proposal'=>proposal_html($order),'invoice'=>invoice_html($order),'agreement'=>$order['includeAgreement']?agreement_html($order):throw new DomainException('No agreement was requested.',404),default=>throw new DomainException('Document not found.',404)};
    $options=new \Dompdf\Options();
    $options->set('isRemoteEnabled',false);
    $options->set('isPhpEnabled',false);
    $options->set('isJavascriptEnabled',false);
    $options->set('chroot',dirname(__DIR__));
    $options->set('tempDir',storage().'/pdf-cache');
    $options->set('fontCache',storage().'/pdf-cache');
    $options->set('defaultFont','DejaVu Sans');
    $pdf=new \Dompdf\Dompdf($options);
    $pdf->setPaper('A4','portrait');
    $pdf->loadHtml($html,'UTF-8');
    $pdf->render();
    $font=$pdf->getFontMetrics()->getFont('DejaVu Sans','normal');
    $pdf->getCanvas()->page_text(38,817,'TopEngineer | '.$order['reference'],$font,7,[.35,.43,.49]);
    $pdf->getCanvas()->page_text(503,817,'{PAGE_NUM} / {PAGE_COUNT}',$font,7,[.35,.43,.49]);
    if($kind==='agreement'&&!$order['agreementApproved']) $pdf->getCanvas()->page_text(400,16,'DRAFT FOR REVIEW',$font,9,[.65,.4,.1]);
    elseif($order['preview']) $pdf->getCanvas()->page_text(445,16,'PREVIEW',$font,9,[.65,.4,.1]);
    return $pdf->output();
}

function render_pack(array $order): string {
    $path=tempnam(storage().'/pdf-cache','pack-');
    try {
        $zip=new ZipArchive();
        if($zip->open($path,ZipArchive::OVERWRITE)!==true) throw new RuntimeException('Could not prepare document package.');
        foreach(public_order($order)['documents'] as $document) $zip->addFromString($document['filename'],render_pdf($order,$document['kind']));
        $zip->close();
        return file_get_contents($path);
    } finally { if(is_file($path)) unlink($path); }
}
