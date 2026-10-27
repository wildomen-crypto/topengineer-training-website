<?php
declare(strict_types=1);

/** A compact, standalone quotation; full course programmes remain a separate PDF. */
function summary_proposal_html(array $order): string {
    $s=$order['seller'];$b=$order['customer'];$q=$order['quote'];
    $country=$order['catalogue']['countries'][$b['country']]??'';
    $recipient=array_filter([$b['companyName'],$b['contactName'],$b['email'],$country],fn($value)=>$value!=='');
    $recipientHtml=$recipient?implode('<br>',array_map('e',$recipient)):'For your training / purchasing team';
    $terms=$order['commercialTerms']??commercial_terms();
    $longRecipient=mb_strlen(implode(' ',$recipient))>300;
    $book=$q['bookSet']??null;
    $compact=$longRecipient || $book!==null;
    $supplierWidth=$longRecipient?'38%':'53%';
    $recipientWidth=$longRecipient?'62%':'47%';
    $introduction=$longRecipient?'Practical, instructor-led Tekla Structures training and reference materials for your selected order.':'Thank you for considering TopEngineer. We offer practical, instructor-led Tekla Structures training tailored to your team\'s selected courses and format.';
    if(!$q['courseCount']) $introduction='Your quotation covers the complete electronic set of three English-language volumes of our Tekla Structures modelling guide.';
    $subtitle=$q['courseCount']?'Live online Tekla Structures training'.($book?' and electronic books':''):'Tekla Structures electronic reference books';
    $logo=base64_encode(file_get_contents(dirname(__DIR__).'/assets/topengineer-logo.png'));
    $signature=base64_encode(file_get_contents(dirname(__DIR__).'/assets/signature-mark.svg'));
    $html='<!doctype html><html lang="en"><head><meta charset="utf-8"><style>
    @page { margin: 28pt 35pt 32pt; }
    body { font-family: "DejaVu Sans",sans-serif; color:#263746; font-size:8.3pt; line-height:1.28; }
    p { margin:0 0 6pt; } h1 { margin:18pt 0 5pt; text-align:center; font-size:19pt; color:#054a85; line-height:1.15; }
    h2 { font-size:10pt; color:#054a85; margin:10pt 0 5pt; }
    table { width:100%; border-collapse:collapse; table-layout:fixed; margin:0 0 6pt; }
    td,th { padding:5pt; vertical-align:top; word-wrap:break-word; }
    .brand td { padding:0; vertical-align:middle; } .brand img { width:185pt; }
    .brand .contact { text-align:right; font-size:8pt; color:#536b7b; }
    .parties td { border:.5pt solid #d3dee6; font-size:'.($longRecipient?'7.1':'7.8').'pt; }
    .label { display:block; color:#607787; font-size:7pt; margin-bottom:3pt; }
    .meta { text-align:center; font-size:7.5pt; color:#536b7b; margin-bottom:11pt; }
    .courses td,.courses th,.extras td,.extras th { border:.6pt solid #9caebc; }
    .courses th,.extras th { background:#eaf2f8; color:#054a85; font-size:7.2pt; text-align:left; }
    .courses td { font-size:8pt; } .courses .level { color:#607787; font-size:7pt; }
    .amount { text-align:right; white-space:nowrap; } .number { text-align:center; }
    .small { font-size:7.3pt; color:#536b7b; } .subtotal { text-align:right; margin:5pt 0 3pt; }
    .total { padding:8pt; background:#eaf2f8; text-align:right; font-size:12pt; color:#054a85; font-weight:bold; margin-bottom:4pt; }
    .extras td { font-size:7pt; padding:4pt; } .extras th { padding:4pt; font-size:6.8pt; }
    .included { border-left:2pt solid #087fe9; padding:1pt 0 1pt 8pt; margin:9pt 0; }
    .signoff { margin-top:10pt; } .signoff td { padding:0; vertical-align:middle; }
    .signoff img { width:97pt; height:36pt; } .footer { font-size:6.6pt; color:#607787; margin-top:8pt; border-top:.5pt solid #d3dee6; padding-top:5pt; }
    .compact .parties td { font-size:6.8pt; line-height:1.12; padding:4pt; }
    .compact h1 { margin-top:8pt; } .compact .signoff { margin-top:4pt; }
    .compact p { margin-bottom:4pt; } .compact .meta { margin-bottom:7pt; }
    .compact h2 { margin:8pt 0 4pt; }
    .compact .courses td,.compact .courses th { padding:3pt; }
    .compact .included { margin:5pt 0; }
    .compact .footer { font-size:6pt; margin-top:5pt; }
    tr { page-break-inside:avoid; } a { color:#054a85; text-decoration:none; }
    </style></head><body'.($compact?' class="compact"':'').' >
    <table class="brand"><tr><td style="width:58%"><img alt="TopEngineer" src="data:image/png;base64,'.$logo.'"></td><td class="contact">'.e($s['email']).'<br>'.e($s['phone']??'+381 61 6139370').'<br>top-engineer.com</td></tr></table>
    <h1>Commercial proposal</h1><p class="meta">'.e($subtitle).'<br>Reference: '.e($order['reference']).' &nbsp; | &nbsp; Issued: '.e(date_label($order['date'])).(!empty($order['validUntil'])?' &nbsp; | &nbsp; Invoice valid until: '.e(date_label($order['validUntil'])):' &nbsp; | &nbsp; Currency: EUR').'</p>
    <table class="parties"><tr><td style="width:'.$supplierWidth.'"><span class="label">FROM</span><strong>'.e($s['legal_name']).'</strong><br>'.e($s['address']).'<br>Business ID (MB): '.e($s['registration_number']).' | Tax ID (PIB): '.e($s['tax_number']).'</td><td style="width:'.$recipientWidth.'"><span class="label">PREPARED FOR</span>'.$recipientHtml.'</td></tr></table>
    <p>'.$introduction.'</p>
    <h2>Your selected items</h2><table class="courses"><thead><tr><th style="width:43%">Course / item</th><th style="width:13%">Format</th><th style="width:10%">Quantity</th><th style="width:17%">Provisional dates</th><th style="width:17%" class="amount">Price</th></tr></thead><tbody>';
    foreach($q['courses'] as $course) {
        $dates=$course['startDate']?date_label($course['startDate']).'<br>'.date_label($course['endDate']):'To be agreed';
        $minimum=$course['billedParticipants']>$course['participants']?'<br><span class="small">Fee for '.$course['billedParticipants'].'</span>':'';
        $html.='<tr><td><span class="level">LEVEL '.$course['id'].'</span><br><strong>'.e($course['name']).'</strong></td><td>'.$course['days'].' days<br>'.$course['hours'].' hours</td><td class="number">'.$course['participants'].'<br><span class="small">'.($course['participants']===1?'person':'people').'</span>'.$minimum.'</td><td class="small">'.$dates.'</td><td class="amount">'.money($course['totalCents']).'</td></tr>';
    }
    if($book) $html.='<tr><td><strong>'.e($book['name']).'</strong><br><span class="small">3 English-language volumes - '.money($book['unitPriceCents']).' per set</span></td><td>Electronic</td><td class="number">'.$book['quantity'].' set'.($book['quantity']===1?'':'s').'</td><td class="small">Not applicable</td><td class="amount">'.money($book['totalCents']).'</td></tr>';
    $html.='</tbody></table>';
    if($q['tax']['approved']) $html.='<p class="small subtotal">Net: '.money($q['netCents']).' &nbsp; | &nbsp; Tax / VAT: '.money($q['taxCents']).'</p>';
    $html.='<div class="total">'.($q['tax']['approved']?'Total for selected items':'Indicative total for selected items').': '.money($q['totalCents']).'</div><p class="small">'.e($q['tax']['note']).'</p>';
    if($q['courseCount']) $html.='<div class="included"><strong>Training includes:</strong> live online instruction, guided practical exercises, preparation support, a personalised digital certificate and brief follow-up questions.<br><span class="small">2 days: essentials, limited practice. 5 days: in-depth training and more practice. 10 days: 5 training days + 5 days on your own pilot project. Software licences are not included.</span></div>';
    if($q['otherCourses']) {
        $html.='<h2>Optional courses - not included in the total</h2><table class="extras"><thead><tr><th style="width:49%">Additional course</th><th style="width:17%" class="amount">2 days / 16 h</th><th style="width:17%" class="amount">5 days / 40 h</th><th style="width:17%" class="amount">10 days / 80 h</th></tr></thead><tbody>';
        foreach($q['otherCourses'] as $extra) $html.='<tr><td>Level '.$extra['id'].' - '.e($extra['name']).'</td><td class="amount">'.money($extra['prices']['2']).'</td><td class="amount">'.money($extra['prices']['5']).'</td><td class="amount">'.money($extra['prices']['10']).'</td></tr>';
        $html.='</tbody></table><p class="small">Optional training prices are for '.$q['comparisonParticipants'].' participant'.($q['comparisonParticipants']===1?'':'s').'. These courses are never added automatically.</p>';
    }
    if($q['courseCount']) $html.='<p class="small"><strong>Planning and terms.</strong> 8 teaching hours per day. For 5- and 10-day formats, the minimum fee covers 3 participants. Complete Level 1 before Levels 2-4; advanced courses can then be taken in any order. Dates are agreed separately; rescheduling does not change the price.</p>';
    $html.='<p class="small">Invoices are valid for '.$terms['validity_months'].' calendar months from issue. '.e($terms['refunds']).' Final price and tax treatment are confirmed in the separate pro forma invoice. This proposal is not a payment document.</p>
    <table class="signoff"><tr><td style="width:77%">Kind regards,<br><strong>'.e($s['director']??'Dmitrii Taran').'</strong> | Director<br>'.e($s['legal_name']).'</td><td><img alt="Decorative signature mark" src="data:image/svg+xml;base64,'.$signature.'"></td></tr></table>
    <p class="footer">Electronically prepared quotation; decorative signature mark. Full course programmes are supplied separately.</p></body></html>';
    return $html;
}
