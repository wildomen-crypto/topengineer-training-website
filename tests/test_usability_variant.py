"""Check the separate local PREVIEW and its downloadable course programmes."""
import json
import re
from pathlib import Path

import fitz
import requests

ROOT = Path(__file__).resolve().parents[1]
BASE = 'http://127.0.0.1:8773'
API = BASE + '/training-order/api.php'


def run():
    session = requests.Session()
    config = session.get(API, timeout=10).json()
    assert config['mode'] == 'preview'
    headers = {'Origin': BASE, 'X-CSRF-Token': config['csrf']}
    courses = [{'id': 1, 'days': 2, 'participants': 1}, {'id': 2, 'days': 5, 'participants': 1}]
    response = session.post(API, params={'action': 'quote'}, json={'courses': courses}, headers=headers, timeout=20)
    response.raise_for_status()
    assert response.json()['totalCents'] == 220000
    response = session.post(API, params={'action': 'proposal'}, json={'courses': courses, 'customer': {}}, headers=headers, timeout=60)
    response.raise_for_status()
    assert response.content.startswith(b'%PDF-') and len(fitz.open(stream=response.content, filetype='pdf')) == 1

    catalogue = json.loads((ROOT / 'work/consulting-usability-version/course-programme.json').read_text(encoding='utf8'))
    for course in catalogue['courses']:
        response = session.get(API, params={'action': 'course-programme', 'level': course['level']}, timeout=60)
        response.raise_for_status()
        pdf = fitz.open(stream=response.content, filetype='pdf')
        assert len(pdf) == 2
        text = '\n'.join(page.get_text() for page in pdf)
        text = ' '.join(re.sub(r'[–—‑]', '-', re.sub(r'-\s*\n\s*', '-', text)).split())
        for part in course['days']:
            for section in part['sections']:
                for code, topic in section['topics']:
                    assert ' '.join(re.sub(r'[–—‑]', '-', topic).split()) in text, (course['level'], code)
        for page in pdf:
            for block in page.get_text('blocks'):
                if block[4].strip():
                    assert block[0] >= 0 and block[1] >= 0 and block[2] <= page.rect.width + 1 and block[3] <= page.rect.height + 1
    assert session.get(API, params={'action': 'course-programme', 'level': '5'}, timeout=10).status_code == 404
    print('Preview calculation, one-page proposal and all four course PDFs passed.')


if __name__ == '__main__':
    run()
