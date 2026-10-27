"""Build a separately maintained usability variant from its own source files."""
from pathlib import Path
import json
import re
import shutil
from bs4 import BeautifulSoup
import build_parallel
from checkout_builder import build_checkout

HERE = Path(__file__).resolve().parent
OUT = build_parallel.OUT


def build():
    build_parallel.build()
    page = BeautifulSoup((OUT / 'index.html').read_text(encoding='utf-8'), 'html.parser')
    page.head.append(BeautifulSoup('<link rel="stylesheet" href="/assets/usability.css?v=3">', 'html.parser'))
    page.body.append(BeautifulSoup('<script src="/assets/usability.js?v=3" defer></script>', 'html.parser'))

    intro = page.select_one('.training-intro__copy > div')
    path = next(p for p in intro.select('p') if 'Recommended learning path:' in p.get_text())
    path.decompose()
    intro.select_one('ol').decompose()
    intro.append(BeautifulSoup('''<p class="training-intro__offer">Live online · 2, 5 or 10 days · From €450 per group for a 2-day course with one participant</p><div class="training-intro__actions"><a class="btn btn-primary" href="#training-calculator">Calculate training price</a><a class="btn btn-outline-primary" href="#course-descriptions">Explore courses</a></div>''', 'html.parser'))
    for row in page.select('.training-intro__facts tr'):
        if row.th and row.th.get_text(strip=True) == 'Payment':
            row.td.string = 'Bank transfer by invoice (when available)'

    for card in page.select('#course-descriptions article'):
        level = card['id'].rsplit('-', 1)[1]
        body = card.select_one('.text-start')
        # The first two elements contain the audience; keep them immediately visible.
        children = [x for x in list(body.children) if getattr(x, 'name', None)]
        assert len(children) >= 6, f'Unexpected card structure {level}'
        details = page.new_tag('details', attrs={'class':'course-details', 'open':''})
        summary = page.new_tag('summary')
        summary.string = 'What you’ll learn and course outcomes'
        details.append(summary)
        children[1].insert_after(details)
        for child in children[2:]: details.append(child.extract())
        actions = card.select_one('.btn-wrap')
        button = page.new_tag('button', attrs={'type':'button', 'class':'btn btn-outline-primary course-choose', 'data-choose-course':level})
        button.string = 'Select course'
        actions.append(button)

    calc = page.select_one('#training-calculator')
    calc.select_one('[data-start-checkout]').string = 'Prepare order documents'
    calc.select_one('[data-download-proposal]').insert_before(BeautifulSoup('<span class="proposal-hint">No company details needed for the proposal.</span>', 'html.parser'))
    for th in calc.select('thead th'):
        if th.get_text(strip=True) == 'Desired start date': th.string = 'Preferred start date (optional)'
    for row in calc.select('[data-course]'):
        level = row['data-course']
        label = row.select_one('.training-quote__start label')
        label.string = 'Preferred start date (optional)'
        date = row.select_one('[data-start-date]')
        date['aria-label'] = f'Preferred start date for Level {level} (optional)'
        note = page.new_tag('small', attrs={'class':'minimum-fee-note', 'data-minimum-fee':'', 'hidden':''})
        note.string = 'Minimum group fee covers up to 3 participants.'
        row.select_one('.training-quote__price').append(note)
    calc.select_one('#quote-date-note').string = 'Start dates are optional. The estimated end date counts all calendar days, including weekends and the start date. Your instructor will confirm the actual schedule.'
    calc.append(BeautifulSoup('''<div class="mobile-quote-bar" data-mobile-quote-bar hidden><div><span>Estimated total</span><strong data-mobile-total>€450.00</strong></div><button type="button" class="btn btn-primary" data-mobile-continue>Prepare documents</button></div>''', 'html.parser'))

    dialog = page.select_one('#course-programme-dialog')
    toolbar = dialog.select_one('.course-programme__toolbar')
    toolbar.append(BeautifulSoup('<nav class="programme-jumps" aria-label="Jump to a programme part"><button type="button" data-jump-part="1">Part 1</button><button type="button" data-jump-part="2">Part 2</button></nav>', 'html.parser'))
    dialog.select_one('.course-programme__footer').insert(0, BeautifulSoup('<a class="programme-download" data-programme-download href="/training-order/api.php?action=course-programme&amp;level=1">Download programme PDF</a>', 'html.parser'))
    for level in range(1, 5):
        heading = page.select_one(f'#inline-course-panel-{level} .parallel-course-heading')
        heading.append(BeautifulSoup(f'<a class="btn btn-outline-primary btn-sm" href="/training-order/api.php?action=course-programme&amp;level={level}">Download programme PDF</a>', 'html.parser'))

    # Avoid the automatically opened third-party chat covering phone and tablet content;
    # existing contact links and the enquiry button remain available.
    for script in page.find_all('script'):
        if script.string and 'crm/site_button/loader_3_i2odr6.js' in script.string:
            script.string.replace_with('if (window.matchMedia("(min-width: 992px)").matches) {\n' + str(script.string) + '\n}')
            break
    else: raise AssertionError('Chat loader not found')
    html = str(page)
    (OUT / 'index.html').write_text(html, encoding='utf-8')
    for name in ['usability.css', 'usability.js']:
        shutil.copy2(HERE / name, OUT / 'assets' / name)
    build_checkout(OUT, html)
    (OUT / 'Start-preview.ps1').write_text("$ProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))\n& (Join-Path $ProjectRoot 'tools/Start-Usability.ps1') @args\n", encoding='utf-8-sig')
    (OUT / 'qa' / 'source-verification.json').write_text(json.dumps({'variant': 'usability', 'base_build_checks_passed': True, 'course_count': 4, 'separate_source': str(HERE.relative_to(build_parallel.ROOT)), 'separate_output': str(OUT.relative_to(build_parallel.ROOT))}, indent=2), encoding='utf-8')
    (OUT / 'README.txt').write_text('Independent usability variant. Start using tools/Start-Usability.ps1 from the repository root. Source: work/consulting-usability-version. Rebuild: python -X utf8 work/consulting-usability-version/build_usability.py.\n', encoding='utf-8')
    print('Usability version built independently.')


if __name__ == '__main__': build()
