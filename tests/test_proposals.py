"""Local PREVIEW only: quotation PDFs, shared customer data and invoice regressions.

Run after starting the preview server: python tests/test_proposals.py
Optional test dependencies: requests and PyMuPDF. No real customer data is used.
"""
from pathlib import Path
import argparse
import calendar
import datetime as dt
import io
import json
import re
import uuid
import zipfile

import fitz
import requests

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / '.runtime/qa-proposal'


def run(base):
    assert base in ['http://127.0.0.1:8771', 'http://localhost:8771'], 'Use the local preview only.'
    QA.mkdir(parents=True, exist_ok=True)
    api = base + '/training-order/api.php'
    session = requests.Session()
    config = session.get(api, timeout=10).json()
    assert config['mode'] == 'preview', 'Never run these synthetic orders against a live checkout.'
    headers = {'X-CSRF-Token': config['csrf'], 'Origin': base}
    checks = []

    def check(label, condition):
        assert condition, label
        checks.append(label)

    def post(action, body, status=200, extra=None):
        result = session.post(api, params={'action': action}, json=body, headers={**headers, **(extra or {})}, timeout=90)
        assert result.status_code == status, (action, result.status_code, result.text[:200])
        return result

    catalogue = json.loads((ROOT / 'outputs/consulting-course-colours/training-order/data/catalogue.json').read_text(encoding='utf-8'))
    line = {'id': 1, 'days': 2, 'participants': 1}
    for days in [2, 5, 10]:
        for people in range(1, 21):
            quote = post('quote', {'courses': [{**line, 'days': days, 'participants': people, 'priceCents': 1}]}).json()
            billed = max(people, catalogue['rates']['minimumBillableParticipants'][str(days)])
            check(f'price {days} days / {people} people', quote['totalCents'] == catalogue['rates']['totalsCents'][str(days)][str(billed)])

    sample_customer = dict(companyName='Example Engineering GmbH', registrationId='TEST-REG-001', vatId='DE-EXAMPLE', contactName='Alex Morgan', email='training@example.com', address='12 Example Street', city='Berlin', postalCode='10115', country='DE', phone='+49 000 000000', poReference='PO-EXAMPLE')

    def pdf_check(result, name):
        (QA / (name + '.pdf')).write_bytes(result.content)
        check(name + ' PDF response', result.headers.get('Content-Type', '').startswith('application/pdf') and result.content.startswith(b'%PDF-'))
        doc = fitz.open(stream=result.content, filetype='pdf')
        check(name + ' fits one A4 page', len(doc) == 1 and 590 < doc[0].rect.width < 600)
        text = ' '.join(doc[0].get_text().split())
        check(name + ' current seller', 'TOPENGINEER LTD DOO' in text and '21781592' in text and '112979992' in text)
        check(name + ' excludes old supplier', '7743840108' not in text and 'Стальпроект' not in text)
        check(name + ' contains no bank instructions', 'IBAN' not in text and 'SWIFT' not in text)
        check(name + ' no missing logo', 'Image not found' not in text)
        (QA / (name + '.pdf')).write_bytes(result.content)
        return doc, text

    for mask in range(1, 16):
        courses = [{**line, 'id': level, 'days': [2, 5, 10, 2][level-1], 'participants': [1, 2, 20, 3][level-1], 'startDate': '2026-12-29'} for level in range(1, 5) if mask & (1 << (level-1))]
        result = post('proposal', {'courses': courses, 'customer': {} if mask == 1 else sample_customer})
        doc, text = pdf_check(result, f'proposal-selection-{mask}')
        for course in courses:
            check(f'selection {mask} includes level {course["id"]}', catalogue['courses'][course['id']-1]['title'] in text)
        check('proposal has its own reference', 'TE-CP-' in result.headers['Content-Disposition'])
        doc.close()

    long_customer = {**sample_customer, 'companyName': 'International ' * 13 + 'Group', 'contactName': 'Alexanderson ' * 12, 'email': 'a'*60+'@' + '.'.join(['b'*60, 'c'*60, 'd'*60, 'com'])}
    result = post('proposal', {'courses': [{**line, 'id': i, 'days': 10, 'participants': 1} for i in range(1, 5)], 'customer': long_customer})
    doc, text = pdf_check(result, 'proposal-long-customer')
    check('long customer retained', long_customer['companyName'].strip() in text and long_customer['email'] in text.replace(' ', ''))
    doc.close()
    post('proposal', {'courses': [line], 'customer': {'email': 'invalid'}}, 422)
    post('proposal', {'courses': [line], 'customer': {'country': 'ZZ'}}, 422)
    post('proposal', {'courses': [{**line, 'days': 3}]}, 422)
    post('proposal', {'courses': [line]}, 403, {'X-CSRF-Token': 'incorrect'})
    post('proposal', {'courses': [line]}, 403, {'Origin': 'https://unrelated.example'})
    check('invalid input and CSRF rejected', True)
    current_config = session.get(api, timeout=10).json()
    check('proposal does not create an order', current_config['resumeAvailable'] == config['resumeAvailable'])

    body = {'courses': [line], 'customer': sample_customer, 'includeAgreement': True, 'businessAuthorised': True}
    quote = post('quote', {'courses': [line], 'country': 'DE'}).json()
    body['quoteFingerprint'] = quote['quoteFingerprint']
    key = str(uuid.uuid4())
    order = post('order', body, 201, {'Idempotency-Key': key}).json()
    again = post('order', body, 201, {'Idempotency-Key': key}).json()
    check('invoice idempotency preserved', order['reference'] == again['reference'])
    check('customer fields inherited unchanged', order['customer'] == sample_customer)
    check('preview payment protection preserved', order['preview'] and order['bank'] is None)
    issued = dt.date.fromisoformat(order['date'])
    month = issued.month - 1 + 6
    expected = dt.date(issued.year + month // 12, month % 12 + 1, min(issued.day, calendar.monthrange(issued.year + month // 12, month % 12 + 1)[1]))
    check('six month validity preserved', order['validUntil'] == expected.isoformat())
    check('separate brief and detailed PDFs', [x['kind'] for x in order['documents']] == ['summary', 'proposal', 'invoice', 'agreement'])
    for kind, pages in [('summary', 1), ('proposal', 10), ('invoice', 1), ('agreement', 2)]:
        response = session.get(api, params={'action': 'document', 'kind': kind}, headers={'Authorization': 'Bearer '+order['token']}, timeout=90)
        response.raise_for_status()
        doc = fitz.open(stream=response.content, filetype='pdf')
        check(kind+' page count', len(doc) == pages)
        raw_text = '\n'.join(page.get_text() for page in doc)
        text = ' '.join(re.sub(r'-\s*\n\s*', '-', raw_text).split())
        check(kind+' uses same company', sample_customer['companyName'] in text and sample_customer['email'] in text)
        if kind == 'proposal':
            for course in catalogue['courses']:
                for part in course['days']:
                    for section in part['sections']:
                        for _, topic in section['topics']:
                            normal = ' '.join(topic.replace('–', '-').replace('—', '-').replace('‑', '-').split())
                            check('programme '+str(course['level'])+' / '+topic, normal in text)
        (QA / ('order-'+kind+'.pdf')).write_bytes(response.content)
    pack = session.get(api, params={'action': 'document', 'kind': 'pack'}, headers={'Authorization': 'Bearer '+order['token']}, timeout=90)
    pack.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(pack.content)) as archive:
        check('ZIP contains both proposals invoice and agreement', len(archive.namelist()) == 4)
    (QA/'checks.json').write_text(json.dumps({'passed': len(checks), 'checks': checks}, indent=2), encoding='utf-8')
    print(json.dumps({'passed': len(checks), 'preview_reference': order['reference'], 'output': str(QA)}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://127.0.0.1:8771')
    run(parser.parse_args().url.rstrip('/'))
