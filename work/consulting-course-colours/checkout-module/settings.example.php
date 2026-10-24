<?php
declare(strict_types=1);
// Copy OUTSIDE the public web root and set TRAINING_ORDER_CONFIG to that path.
// Never enable live payment requests until bank details and tax rules are confirmed.
return [
    'mode' => 'preview',
    'allowed_origins' => ['http://127.0.0.1:8771', 'http://localhost:8771', 'https://top-engineer.com'],
    'seller' => [
        'legal_name' => 'TOPENGINEER LTD DOO',
        'address' => 'KOSOVSKA 17 sp.5 st.7, BEOGRAD-STARI GRAD, Serbia',
        'registration_number' => '21781592',
        'tax_number' => '112979992',
        'country' => 'RS',
        'email' => 'info@top-engineer.com',
        'director' => 'Dmitrii Taran',
        'website' => 'https://top-engineer.com',
        'details_confirmed' => false,
    ],
    'bank' => [
        'beneficiary' => 'TOPENGINEER LTD DOO',
        'iban' => '',
        'swift' => '',
        'name' => '',
        'address' => '',
        'correspondent' => '',
        'currency' => 'EUR',
        'details_confirmed' => false,
    ],
    // Price treatment must be confirmed by your accountant. No automatic VAT exemption.
    // mode: unconfigured | outside_scope | exempt | exclusive | inclusive
    // rate_bps: 2000 = 20%; note: the accountant-approved explanation on the invoice.
    'tax_rules' => [
        'foreign_business' => ['approved' => false, 'mode' => 'unconfigured', 'rate_bps' => 0, 'note' => ''],
        'RS' => ['approved' => false, 'mode' => 'unconfigured', 'rate_bps' => 0, 'note' => ''],
    ],
    'agreement_approved' => false,
    'agreement_version' => 'draft-2026-10-24',
    'commercial_terms' => [
        'validity_months' => 6,
        'rescheduling' => 'Changing the training dates does not change the training fee.',
        'refunds' => 'If you request a refund, we refund your payment less bank commissions. No other cancellation fee is deducted.',
    ],
    // The owner has not yet confirmed a prepayment percentage or incoming bank fee allocation.
    'payment_terms_approved' => false,
    'payment_term' => 'Payment terms will be confirmed separately. Training dates are agreed separately.',
];
