"""PREVIEW-only regression checks for optional electronic books and PDF layouts.

Start tools/Start-Card-Selection.ps1 first; run python tests/test_book_orders.py.
All customer details are synthetic. QA documents stay in the ignored .runtime folder.
"""
from pathlib import Path
import json
import re
import uuid

import fitz
import requests

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / '.runtime/qa-books'
BASE = 'http://127.0.0.1:8774'
API = BASE + '/training-order/api.php'
QA.mkdir(parents=True, exist_ok=True)
session = requests.Session()
config = session.get(API, timeout=15).json()
assert config['mode'] == 'preview', 'Synthetic orders must never reach a live checkout.'
headers = {'X-CSRF-Token': config['csrf'], 'Origin': BASE}
checks = []


def check(name, condition):
    assert condition, name
    checks.append(name)


def post(action, body, status=200, extra=None):
    response = session.post(API, params={'action': action}, json=body,
                            headers={**headers, **(extra or {})}, timeout=90)
    assert response.status_code == status, (action, response.status_code, response.text[:250])
    return response


def inspect_pdf(response, label, pages=1, save=False):
    assert response.content.startswith(b'%PDF-'), label
    doc = fitz.open(stream=response.content, filetype='pdf')
    if save or (pages is not None and len(doc) != pages):
        (QA / (label + '.pdf')).write_bytes(response.content)
        for number, page in enumerate(doc):
            page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(QA / (label + f'-{number+1}.png'))
    if pages is not None:
        check(label + ' page count', len(doc) == pages)
    text = ' '.join(re.sub(r'-\s*\n\s*', '-', '\n'.join(p.get_text() for p in doc)).split())
    check(label + ' includes electronic books', 'Electronic' in text and 'modelling guide' in text)
    check(label + ' no missing images', 'Image not found' not in text)
    for page in doc:
        spans = [s for b in page.get_text('dict')['blocks'] if 'lines' in b
                 for line in b['lines'] for s in line['spans'] if s['text'].strip()]
        check(label + ' text within page', all(16 <= s['bbox'][0] and s['bbox'][2] <= page.rect.width - 16
                                               and 8 <= s['bbox'][1] and s['bbox'][3] <= page.rect.height - 8
                                               for s in spans))
    doc.close()
    return text


line = {'id': 1, 'days': 2, 'participants': 1}
catalogue = json.loads((ROOT / 'outputs/consulting-card-selection-version/training-order/data/catalogue.json').read_text(encoding='utf8'))
for days in [2, 5, 10]:
    for participants in [1, 2, 3, 20]:
        course = {**line, 'days': days, 'participants': participants}
        plain = post('quote', {'courses': [course]}).json()
        books = post('quote', {'courses': [course], 'bookQuantity': 2, 'unitPriceCents': 1}).json()
        check(f'{days} days / {participants} people: add exactly two book sets', books['totalCents'] == plain['totalCents'] + 17800)
        check('books do not change teaching duration', books['hours'] == plain['hours'] and books['days'] == plain['days'])
        check('book price is authoritative', books['bookSet']['unitPriceCents'] == 8900)

books_only = post('quote', {'courses': [], 'bookQuantity': 1, 'country': 'DE'}).json()
check('books-only quote', books_only['totalCents'] == 8900 and books_only['courseCount'] == 0 and books_only['hours'] == 0)
check('books-only has no training prerequisite', not books_only['needsPrerequisiteConfirmation'])
check('books tax requires separate approval before live payments', not books_only['paymentReady'])
for quantity in [-1, 21, 1.5, '1', True]:
    post('quote', {'courses': [line], 'bookQuantity': quantity}, 422)
post('quote', {'courses': [], 'bookQuantity': 0}, 422)
post('quote', {'courses': [{**line, 'days': 3}], 'bookQuantity': 1}, 422)
post('proposal', {'courses': [line], 'bookQuantity': 1}, 403, {'X-CSRF-Token': 'incorrect'})
check('invalid quantities, course data and CSRF are rejected', True)

customer = dict(companyName='Example Engineering GmbH', registrationId='TEST-REG-001', vatId='DE-EXAMPLE',
                contactName='Alex Morgan', email='training@example.com', address='12 Example Street',
                city='Berlin', postalCode='10115', country='DE', phone='', poReference='PO-EXAMPLE')
maximum = {**customer, 'companyName': 'W'*200, 'contactName': 'M'*160,
           'email': 'a'*64+'@'+'b'*63+'.'+'c'*63+'.'+'d'*57+'.com', 'country': 'GS'}
for mask in range(16):
    courses = [{**line, 'id': level, 'days': [2, 5, 10, 2][level-1],
                'participants': [1, 2, 20, 3][level-1], 'startDate': '2026-12-29'}
               for level in range(1, 5) if mask & (1 << (level-1))]
    pdf = post('proposal', {'courses': courses, 'bookQuantity': 1, 'customer': customer})
    text = inspect_pdf(pdf, f'proposal-selection-{mask}', save=mask == 15)
    check('proposal retains footer', 'Electronically prepared quotation' in text)
    for course in courses:
        check('proposal retains selected course', catalogue['courses'][course['id']-1]['title'] in text)

courses = [{**line, 'id': n, 'days': 10, 'participants': 20, 'startDate': '2026-12-29'} for n in range(1, 5)]
body = {'courses': courses, 'bookQuantity': 20, 'customer': maximum}
inspect_pdf(post('proposal', body), 'proposal-maximum-details', save=True)
inspect_pdf(post('proposal', {'courses': [], 'bookQuantity': 1, 'customer': {}}), 'proposal-books-only', save=True)
quote = post('quote', {**body, 'country': 'GS'}).json()
order_body = {**body, 'quoteFingerprint': quote['quoteFingerprint'], 'includeAgreement': True,
              'businessAuthorised': True, 'prerequisiteConfirmed': True}
key = str(uuid.uuid4())
order = post('order', order_body, 201, {'Idempotency-Key': key}).json()
repeated = post('order', order_body, 201, {'Idempotency-Key': key}).json()
check('same order remains idempotent', order['reference'] == repeated['reference'])
check('books and customer are snapshotted', order['quote']['bookSet']['quantity'] == 20 and order['customer'] == maximum)
check('preview payment protection preserved', order['preview'] and order['bank'] is None)
check('correct maximum total', order['quote']['totalCents'] == 4*1200000 + 20*8900)
changed = {**body, 'bookQuantity': 19}
changed_quote = post('quote', {**changed, 'country': 'GS'}).json()
post('order', {**order_body, 'bookQuantity': 19, 'quoteFingerprint': changed_quote['quoteFingerprint']}, 409, {'Idempotency-Key': key})
check('changed quantity cannot silently reuse an order reference', True)
for kind in ['invoice', 'summary', 'proposal', 'agreement']:
    result = session.get(API, params={'action': 'document', 'kind': kind},
                         headers={'Authorization': 'Bearer ' + order['token']}, timeout=90)
    result.raise_for_status()
    text = inspect_pdf(result, 'order-' + kind, pages=1 if kind in ['invoice', 'summary'] else None, save=kind == 'invoice')
    check(kind + ' retains books and order total', 'EUR 1,780.00' in text and 'EUR 49,780.00' in text)

books_order_body = {'courses': [], 'bookQuantity': 1, 'customer': customer,
                    'quoteFingerprint': books_only['quoteFingerprint'], 'businessAuthorised': True}
books_order = post('order', books_order_body, 201, {'Idempotency-Key': str(uuid.uuid4())}).json()
check('books can be ordered without training', books_order['quote']['courseCount'] == 0)
post('order', {**books_order_body, 'includeAgreement': True}, 422, {'Idempotency-Key': str(uuid.uuid4())})
print(json.dumps({'passed': len(checks), 'qa_directory': str(QA)}, indent=2))
(QA / 'checks.json').write_text(json.dumps(checks, indent=2), encoding='utf8')
