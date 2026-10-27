"""Build the independent variant from its own frozen page and curriculum data."""
from pathlib import Path
import hashlib
import json
import re
import shutil
from bs4 import BeautifulSoup

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SETTINGS = json.loads((HERE / 'variant.json').read_text(encoding='utf-8'))
OUT = ROOT / SETTINGS['output']
PORT = SETTINGS['port']
THEME = SETTINGS.get('theme')
ORIGINAL = ROOT / 'outputs/consulting-table-version'
QA = OUT / 'qa'


def hashes(folder):
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob('*')) if p.is_file() and 'qa' not in p.relative_to(folder).parts}


def initialise():
    # Initial snapshot only. Later builds do not import the previous site's edits.
    if (HERE / 'base-page.html').exists():
        return
    source = ROOT / 'work/consulting-table-version'
    for name in ['programme_renderer.py', 'course-programme.json', 'programme-translation-review.json']:
        shutil.copy2(source / name, HERE / ('programme_base.py' if name == 'programme_renderer.py' else name))
    shutil.copy2(ORIGINAL / 'index.html', HERE / 'base-page.html')
    if OUT.exists():
        raise RuntimeError('Choose a fresh output directory before taking the first snapshot.')
    shutil.copytree(ORIGINAL, OUT, ignore=shutil.ignore_patterns('qa', 'README.txt', 'design-qa.md', 'Start-preview.ps1'))


def build():
    before = hashes(ORIGINAL) if ORIGINAL.exists() else {}
    initialise()
    from parallel_renderer import render_course_programmes, render_programme_dialog
    from programme_base import programmes
    from calculator_defaults import calculator_markup, description_markup, programme_tabs_markup
    from training_formats import insert_training_formats
    from certificate_gallery import replace_certificate_section
    html = (HERE / 'base-page.html').read_text(encoding='utf-8')
    html, count = re.subn(r'<section id="course-programmes".*?</section>', lambda _: programme_tabs_markup(render_course_programmes()), html, count=1, flags=re.S)
    assert count == 1
    html, count = re.subn(r'<dialog class="course-programme".*?</dialog>', lambda _: render_programme_dialog(), html, count=1, flags=re.S)
    assert count == 1
    html, count = re.subn(r'<section\b(?=[^>]*\bid="training-calculator")[^>]*>.*?</section>', lambda match: calculator_markup(match[0]), html, count=1, flags=re.S)
    assert count == 1
    for level in range(1, 5):
        html, count = re.subn(rf'<article\b(?=[^>]*\bid="original-course-level-{level}")[^>]*>.*?</article>', lambda match: description_markup(match[0], level), html, count=1, flags=re.S)
        assert count == 1
    html = insert_training_formats(html)
    html = replace_certificate_section(html)
    theme_link = f'<link rel="stylesheet" href="/assets/{THEME}?v=20261023-1">\n' if THEME else ''
    html = html.replace('</head>', '<link rel="stylesheet" href="/assets/parallel-days.css?v=20261023-1">\n<link rel="stylesheet" href="/assets/course-levels.css?v=20261023-neutral-2">\n<link rel="stylesheet" href="/assets/certificate-gallery.css?v=20261023-3">\n' + theme_link + '</head>', 1)
    html, count = re.subn(r'<script\b[^>]*\bsrc="/assets/table-calculator\.js[^>]*></script>', lambda match: '<script src="/assets/document-tools.js?v=20261026-1" defer></script>\n'+match[0], html, count=1)
    assert count == 1
    html = re.sub(r'table-calculator\.css\?v=[^"\s]+', 'table-calculator.css?v=20261023-compact-prices-1', html)
    html = re.sub(r'course-programme(s?)\.js\?v=[^"\s]+', r'course-programme\1.js?v=20261023-parts-1', html)
    html = re.sub(r'table-calculator\.js\?v=[^"\s]+', 'table-calculator.js?v=20261026-proposal-1', html)
    html = re.sub(r'<title>.*?</title>', '<title>' + SETTINGS['title'] + '</title>', html, count=1, flags=re.S)
    for name in ['course-programmes.js', 'course-programme.js', 'parallel-days.css', 'table-calculator.js', 'table-calculator.css', 'course-levels.css', 'certificate-gallery.css'] + ([THEME] if THEME else []):
        shutil.copy2(HERE / name, OUT / 'assets' / name)
    for asset in (HERE / 'certificate-assets').glob('topengineer-certificate-*-days.*'):
        shutil.copy2(asset, OUT / 'assets' / asset.name)
    shutil.copy2(HERE / 'certificate-assets' / 'generation-notes.json', OUT / 'assets' / 'certificate-generation-notes.json')
    shutil.copy2(HERE / 'certificate-assets' / 'certificate-image-notes.md', OUT / 'assets' / 'certificate-image-notes.md')
    (OUT / 'index.html').write_text(html, encoding='utf-8')
    (OUT / 'Start-preview.ps1').write_text(f"$PreviewRoot = Split-Path -Parent $MyInvocation.MyCommand.Path\nSet-Location -LiteralPath $PreviewRoot\npython -m http.server {PORT} --bind 127.0.0.1\n", encoding='utf-8-sig')
    (OUT / 'README.txt').write_text(f'''TOPENGINEER — {SETTINGS['label']}

Это готовая текущая цветная версия самостоятельного проекта.
Для запуска из корня репозитория: Start-Windows.cmd.
Или из этой папки: powershell.exe -NoProfile -ExecutionPolicy Bypass -File Start-preview.ps1
Оставить окно сервера открытым; PHP нужен для формы и PDF.

Главная: http://127.0.0.1:{PORT}/
Калькулятор: http://127.0.0.1:{PORT}/#training-calculator
Программы: http://127.0.0.1:{PORT}/#course-programmes
Форма реквизитов: http://127.0.0.1:{PORT}/training-order/
При занятом порте из корня: powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/Start-Windows.ps1 -Port 8774

Начальный расчёт: Level 1, 2 дня, 1 участник, EUR 450.
Четыре курса, 352 темы. Part 1 и Part 2 одновременно видны на широком экране.
Режим документов PREVIEW. Реальные банковские инструкции не включены.

Для Codex: открыть корень репозитория и прочитать AGENTS.md, CODEX_HANDOFF.md,
PROJECT_CONTEXT.md и README.md. Старые версии и прежний компьютер не нужны.
Исходники: work/{HERE.name}/. Не редактировать только готовый outputs.
Пересборка из корня: python -X utf8 work/{HERE.name}/build_parallel.py
''', encoding='utf-8-sig')
    from checkout_builder import build_checkout
    build_checkout(OUT, html)
    soup = BeautifulSoup(html, 'html.parser')
    ids = [item['id'] for item in soup.select('[id]')]
    assert len(ids) == len(set(ids)), 'Duplicate IDs'
    for course in programmes():
        for day in course['days']:
            expected = [topic for section in day['sections'] for topic in section['topics']]
            for prefix in ['inline', 'programme']:
                panel = soup.select_one(f'#{prefix}-day-panel-{course["level"]}-{day["day"]}')
                actual = [[span.get_text() for span in li.find_all('span', recursive=False)] for li in panel.select('li')]
                assert actual == expected, 'Topic text or order changed'
                assert not panel.has_attr('hidden'), 'A day should not be hidden'
    # Compare all page content outside the explicitly edited regions.
    base = BeautifulSoup((HERE / 'base-page.html').read_text(encoding='utf-8'), 'html.parser')
    old_section = base.select_one('#course-programmes')
    old_section.replace_with(soup.select_one('#course-programmes').__copy__())
    old_dialog = base.select_one('#course-programme-dialog')
    old_dialog.replace_with(soup.select_one('#course-programme-dialog').__copy__())
    base.select_one('#training-calculator').replace_with(soup.select_one('#training-calculator').__copy__())
    base.select_one('#before-training').insert_before(soup.select_one('#training-formats').__copy__())
    base.select_one('#course-certificate').replace_with(soup.select_one('#course-certificate').__copy__())
    for level in range(1, 5):
        selector = f'#original-course-level-{level}'
        base.select_one(selector).replace_with(soup.select_one(selector).__copy__())
    for name in ['#training-calculator', '#course-descriptions', '#training-rates']:
        assert str(base.select_one(name)) == str(soup.select_one(name)), name + ' changed'
    base.title.string = soup.title.string
    base.select_one('link[href^="/assets/table-calculator.css"]')['href'] = soup.select_one('link[href^="/assets/table-calculator.css"]')['href']
    for script in base.select('script[src]'):
        script['src'] = re.sub(r'course-programme(s?)\.js\?v=[^"\s]+', r'course-programme\1.js?v=20261023-parts-1', script['src'])
        script['src'] = re.sub(r'table-calculator\.js\?v=[^"\s]+', 'table-calculator.js?v=20261026-proposal-1', script['src'])
    # Ignore whitespace around the single added stylesheet when comparing the rest.
    comparable = BeautifulSoup(html, 'html.parser')
    comparable.select_one('link[href^="/assets/parallel-days.css"]').decompose()
    comparable.select_one('link[href^="/assets/course-levels.css"]').decompose()
    comparable.select_one('link[href^="/assets/certificate-gallery.css"]').decompose()
    if THEME:
        comparable.select_one(f'link[href^="/assets/{THEME}"]').decompose()
    comparable.select_one('script[src^="/assets/document-tools.js"]').decompose()
    normalise = lambda page: re.sub(r'>\s+<', '><', str(page))
    assert normalise(base) == normalise(comparable), 'Unrelated page content changed'
    assert hashes(ORIGINAL) == before, 'Previous site was modified'
    inherited = hashes(ORIGINAL)
    copied = hashes(OUT)
    changed = [name for name in inherited if name in copied and inherited[name] != copied[name]]
    if ORIGINAL.exists():
        assert sorted(changed) == sorted(['index.html', 'assets/course-programme.js', 'assets/course-programmes.js', 'assets/table-calculator.js', 'assets/table-calculator.css', 'README.txt', 'Start-preview.ps1'])
    QA.mkdir(exist_ok=True)
    proof = {'previous_site_unchanged': True, 'unrelated_html_unchanged': True, 'independent_assets': True, 'topics_exactly_preserved': 352,
             'both_parts_visible': True, 'programme_independent_of_duration': True, 'changed_existing_files': changed,
             'initial_quote': {'level': 1, 'participants': 1, 'days': 2, 'total_eur': 450},
             'colour_theme': THEME or 'original-blue',
             'training_formats': [2, 5, 10], 'pilot_project_belongs_to_customer': True,
             'training_format_cards_use_only_original_and_bootstrap_styles': True,
             'certificate_durations': [2, 5, 10], 'certificate_sheets_responsive_overlap': True,
             'new_stylesheets': ['assets/parallel-days.css', 'assets/course-levels.css', 'assets/certificate-gallery.css'] + ([f'assets/{THEME}'] if THEME else [])}
    (QA / 'source-verification.json').write_text(json.dumps(proof, indent=2), encoding='utf-8')
    (QA / 'original-site-hashes.json').write_text(json.dumps(before, indent=2), encoding='utf-8')
    print(json.dumps(proof, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    build()
