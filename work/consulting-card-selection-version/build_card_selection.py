"""Build the selectable-card variant without changing other versions."""
from pathlib import Path
from copy import deepcopy
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
    page.head.append(BeautifulSoup('<link rel="stylesheet" href="/assets/card-selection.css?v=9">', 'html.parser'))
    page.body.append(BeautifulSoup('<script src="/assets/card-selection.js?v=2" defer></script>', 'html.parser'))
    books = BeautifulSoup((HERE / 'training-books.html').read_text(encoding='utf8'), 'html.parser')
    page.select_one('#training-formats').insert_before(books)
    product = json.loads((HERE / 'book-product.json').read_text(encoding='utf8'))
    unit_price = f"€{product['unitPriceCents']/100:.0f}"
    page.select_one('[data-book-unit-price]').string = unit_price
    data = page.new_tag('script', attrs={'type':'application/json', 'id':'training-book-product'})
    data.string = json.dumps(product, ensure_ascii=False).replace('<', '\\u003c')
    page.select_one('#training-rates').insert_after(data)
    options = ''.join(f'<option value="{n}">{n} set{"s" if n != 1 else ""}</option>' for n in range(1, product['maxQuantity']+1))
    book_row = BeautifulSoup(f'''<tr class="training-quote__books is-selected" data-book-row>
      <td class="training-quote__select"><label class="training-quote__check-target"><input class="training-quote__checkbox" type="checkbox" checked data-book-selected aria-label="Add the electronic book set"><span class="visually-hidden">Add book set</span></label></td>
      <td colspan="5" class="training-quote__book-details"><div class="training-quote__book-content"><div><strong class="training-quote__title">{product['name']}</strong><span class="small text-muted">{product['description']} · {unit_price} per set</span> <a class="training-quote__programme-link" href="#training-books">About the books</a></div><div class="training-quote__book-quantity"><label class="small" for="quote-book-quantity">Number of sets</label><select class="form-select" id="quote-book-quantity" data-book-quantity>{options}</select></div></div></td>
      <td class="training-quote__price"><span class="training-quote__mobile-label">Book price</span><output data-book-price>€{product['unitPriceCents']/100:,.2f}</output></td>
    </tr>''', 'html.parser')
    calculator = page.select_one('#training-calculator')
    # Keep the utility links above the frame; the border starts at the column headings.
    quote = calculator.select_one('.training-quote')
    quote.insert_before(quote.select_one('.training-quote__heading').extract())
    calculator.select_one('tbody').append(book_row)
    rates = json.loads(page.select_one('#training-rates').string)
    initial_total_cents = rates['totalsCents']['2']['1'] + product['unitPriceCents']
    initial_total = f'€{initial_total_cents/100:,.2f}'
    calculator.select_one('[data-quote-total]').string = initial_total
    calculator.select_one('[data-total-meta]').string = '1 course · 2 days · 16 hours · 1 book set'
    calculator.select_one('[data-mobile-total]').string = initial_total
    # End the framed table after the book row. Keep its live total and notes together
    # directly below it, with no surrounding border or background fill.
    footer = calculator.select_one('tfoot')
    summary = page.new_tag('div', attrs={'class':'training-quote__summary'})
    summary.append(footer.select_one('.training-quote__total').extract())
    notes = page.new_tag('div', attrs={'class':'training-quote__notes'})
    notes.append(calculator.select_one('#quote-date-note').extract())
    notes.append(calculator.select_one('.training-quote__actions > p').extract())
    summary.append(notes)
    quote.insert_after(summary)
    footer.decompose()
    calculator.select_one('.training-quote__total strong').string = 'Total for selected items'
    calculator.select_one('thead th:nth-child(2)').string = 'Course / item'
    calculator.select_one('thead th:last-child').string = 'Group / item price'
    calculator.select_one('.section-title p').string = 'Select your courses, duration and group size. Add an electronic book set if you need one.'
    for stylesheet in page.select('link[href]'):
        if '/assets/table-calculator.css' in stylesheet['href']:
            stylesheet['href'] = '/assets/table-calculator.css?v=20261027-white-header-1'
    for script in page.select('script[src]'):
        if '/assets/table-calculator.js' in script['src']: script['src'] = '/assets/table-calculator.js?v=20261027-books-1'
        if '/assets/document-tools.js' in script['src']: script['src'] = '/assets/document-tools.js?v=20261027-books-1'
        if '/assets/usability.js' in script['src']: script['src'] = '/assets/usability.js?v=20261027-books-1'
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
    # Keep the background experiment on its own page. The introduction and course
    # descriptions stay white; subsequent modules alternate using the theme's colour.
    alternate = deepcopy(page)
    alternate.title.string = 'TopEngineer | Training - alternating section backgrounds'
    for section_id in ['training-calculator', 'training-books', 'before-training',
                       'after-training-support']:
        alternate.find(id=section_id)['class'].append('section-bg')
    (OUT / 'alternating-backgrounds.html').write_text(str(alternate), encoding='utf8')
    scrolling = deepcopy(page)
    scrolling.title.string = 'TopEngineer | Training - background follows your reading'
    scrolling.body['data-scroll-background'] = ''
    scrolling.head.append(BeautifulSoup('<link rel="stylesheet" href="/assets/scroll-background.css?v=1">', 'html.parser'))
    scrolling.body.append(BeautifulSoup('<script src="/assets/scroll-background.js?v=1" defer></script>', 'html.parser'))
    (OUT / 'scroll-background.html').write_text(str(scrolling), encoding='utf8')
    # The current page stays white, with three static section highlights.
    # Apply it after producing the independent background experiments above.
    for section_id in ['how-training-works', 'training-formats', 'course-certificate']:
        page.find(id=section_id)['class'].append('section-bg')
    (OUT / 'index.html').write_text(str(page), encoding='utf8')
    for name in ['card-selection.css', 'card-selection.js', 'scroll-background.css', 'scroll-background.js']:
        shutil.copy2(HERE / name, OUT / 'assets' / name)
    for level in range(1, 4):
        name = f'tekla-guide-volume-{level}.jpg'
        shutil.copy2(HERE / 'book-assets' / name, OUT / 'assets' / name)
    (OUT / 'Start-preview.ps1').write_text("$ProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))\n& (Join-Path $ProjectRoot 'tools/Start-Card-Selection.ps1') @args\n", encoding='utf-8-sig')
    (OUT / 'README.txt').write_text('Independent selectable-course-cards variant. Start from project root with tools/Start-Card-Selection.ps1. Source: work/consulting-card-selection-version. Rebuild: python -X utf8 work/consulting-card-selection-version/build_card_selection.py.\n', encoding='utf8')
    (OUT / 'qa' / 'source-verification.json').write_text(json.dumps({'variant':'selectable-course-cards', 'course_count':4, 'independent_source':str(HERE.relative_to(build_parallel.ROOT)), 'independent_output':str(OUT.relative_to(build_parallel.ROOT))},indent=2),encoding='utf8')
    print('Selectable-card version built independently.')


if __name__ == '__main__': build()
