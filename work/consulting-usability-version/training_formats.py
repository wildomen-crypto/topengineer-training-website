"""Source-backed duration comparison and compact labels shared with the quote."""
from html import escape
from pathlib import Path
import json
import re

HERE = Path(__file__).resolve().parent


def format_data():
    return json.loads((HERE / 'training-formats.json').read_text(encoding='utf-8'))


def render_training_formats():
    data = format_data()
    cards = []
    for item in data['formats']:
        days = item['days']
        split = f'<p class="fw-bold mb-3">{escape(item["split"])}</p>' if item.get('split') else ''
        paragraphs = ''.join(f'<p class="mb-3">{escape(text)}</p>' for text in item['paragraphs'])
        popularity = f'<div class="btn-wrap mt-auto"><p class="small mb-0">{escape(item["popularity"])}</p></div>' if item.get('popularity') else ''
        ribbon = '<span class="advanced bg-primary text-center">Popular</span>' if days == 10 else ''
        cards.append(f'''<div class="col-lg-4 d-flex"><article id="training-format-{days}" class="box featured d-flex flex-column w-100 text-start" aria-labelledby="training-format-{days}-title">{ribbon}
  <h3 id="training-format-{days}-title" class="text-center">{days} days<span class="d-block small fw-normal mt-1">{days * data['hoursPerDay']} hours</span></h3>
  <p class="h5 fw-bold mb-3">{escape(item['title'])}</p>{split}{paragraphs}{popularity}
</article></div>''')
    metadata = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    return f'''<section id="training-formats" class="row pricing px-4 px-md-5 pt-5 pb-5" aria-labelledby="training-formats-title"><div class="container">
  <div class="section-title pt-4"><h2 id="training-formats-title">{escape(data['heading'])}</h2><p>{escape(data['introduction'])}</p></div>
  <div class="row g-4">{''.join(cards)}</div>
  <p class="text-end mt-3 mb-0"><a href="#training-calculator" class="btn btn-outline-primary btn-sm">Back to calculator <i class="bi bi-arrow-up" aria-hidden="true"></i></a></p>
  <script type="application/json" id="training-formats-data">{metadata}</script>
</div></section>'''


def insert_training_formats(html):
    pattern = r'<section\b(?=[^>]*\bid="before-training")[^>]*>'
    updated, count = re.subn(pattern, lambda match: render_training_formats() + '\n' + match[0], html, count=1)
    assert count == 1, 'The preparation section could not be identified.'
    return updated
