"""Build the selectable-card variant without changing other versions."""
from pathlib import Path
import json
import shutil
from bs4 import BeautifulSoup
import build_usability
import build_parallel

HERE = Path(__file__).resolve().parent
OUT = build_parallel.OUT


def build():
    build_usability.build()
    page = BeautifulSoup((OUT / 'index.html').read_text(encoding='utf8'), 'html.parser')
    page.head.append(BeautifulSoup('<link rel="stylesheet" href="/assets/card-selection.css?v=4">', 'html.parser'))
    page.body.append(BeautifulSoup('<script src="/assets/card-selection.js?v=2" defer></script>', 'html.parser'))
    books = BeautifulSoup((HERE / 'training-books.html').read_text(encoding='utf8'), 'html.parser')
    page.select_one('#training-formats').insert_before(books)
    intro = page.select_one('#course-descriptions .section-title p')
    intro.string = 'Select the courses you need. Complete Level 1 first, then take Levels 2–4 in any order to suit your work.'
    for level in range(1, 5):
        card = page.select_one(f'#original-course-level-{level}')
        card['data-selectable-card'] = str(level)
        card.select_one('[data-choose-course]').decompose()
        initial = ' checked' if level == 1 else ''
        control = BeautifulSoup(f'''<label class="course-card-choice"><input type="checkbox" data-card-choice="{level}" aria-label="Select Level {level} course"{initial}></label>''', 'html.parser')
        card.select_one('h3 .course-level').insert_before(control)
        if level == 1: card['class'].append('course-card-selected')
    (OUT / 'index.html').write_text(str(page), encoding='utf8')
    for name in ['card-selection.css', 'card-selection.js']:
        shutil.copy2(HERE / name, OUT / 'assets' / name)
    shutil.copy2(HERE / 'book-assets' / 'tekla-modelling-guide-three-volumes.jpg', OUT / 'assets' / 'tekla-modelling-guide-three-volumes.jpg')
    (OUT / 'Start-preview.ps1').write_text("$ProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))\n& (Join-Path $ProjectRoot 'tools/Start-Card-Selection.ps1') @args\n", encoding='utf-8-sig')
    (OUT / 'README.txt').write_text('Independent selectable-course-cards variant. Start from project root with tools/Start-Card-Selection.ps1. Source: work/consulting-card-selection-version. Rebuild: python -X utf8 work/consulting-card-selection-version/build_card_selection.py.\n', encoding='utf8')
    (OUT / 'qa' / 'source-verification.json').write_text(json.dumps({'variant':'selectable-course-cards', 'course_count':4, 'independent_source':str(HERE.relative_to(build_parallel.ROOT)), 'independent_output':str(OUT.relative_to(build_parallel.ROOT))},indent=2),encoding='utf8')
    print('Selectable-card version built independently.')


if __name__ == '__main__': build()
