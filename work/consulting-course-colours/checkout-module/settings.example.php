<?php
declare(strict_types=1);
// Copy OUTSIDE the public web root and set TRAINING_ORDER_CONFIG to that path.
// Never enable live payment requests until bank details and tax rules are confirmed.
return [
    'mode' => 'preview',
    'allowed_origins' => ['http://127.0.0.1:8771', 'http://localhost:8771', 'https://top-engineer.com'],
    'seller' => [
        'legal_name' => 'Topengineer LTD doo Beograd',
        'address' => 'Kosovska 17, 11000 Beograd (Stari Grad), Serbia',
        'registration_number' => '21781592',
        'tax_number' => '112979992',
        'country' => 'RS',
        'email' => 'info@top-engineer.com',
        'website' => 'https://top-engineer.com',
        'details_confirmed' => false,
    ],
    'bank' => [
        'beneficiary' => 'Topengineer LTD doo Beograd',
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
    'agreement_version' => 'draft-2026-10-23',
    'payment_term' => 'Payment is required before training begins. Training dates are agreed separately.',
];
