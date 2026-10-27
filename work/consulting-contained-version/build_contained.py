"""Build the independent centred-page variant from its own frozen source."""
from pathlib import Path
import json
import shutil
from bs4 import BeautifulSoup
import build_card_selection
import build_parallel

HERE = Path(__file__).resolve().parent
OUT = build_parallel.OUT


def build():
    build_card_selection.build()
    for relative in ['index.html', 'training-order/index.html']:
        page = BeautifulSoup((OUT / relative).read_text(encoding='utf8'), 'html.parser')
        page.body['class'] = [*page.body.get('class', []), 'contained-site']
        page.head.append(BeautifulSoup('<link rel="stylesheet" href="/assets/contained-layout.css?v=1">', 'html.parser'))
        (OUT / relative).write_text(str(page), encoding='utf8')
    shutil.copy2(HERE / 'contained-layout.css', OUT / 'assets/contained-layout.css')
    (OUT / 'Start-preview.ps1').write_text("$ProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))\n& (Join-Path $ProjectRoot 'tools/Start-Contained.ps1') @args\n", encoding='utf-8-sig')
    (OUT / 'README.txt').write_text('Independent centred layout, max width 1600 px. Start from the repository root with tools/Start-Contained.ps1 (port 8775). Source: work/consulting-contained-version. Rebuild: python -X utf8 work/consulting-contained-version/build_contained.py. The original selectable-card version on port 8774 is separate.\n', encoding='utf8')
    (OUT / 'qa/source-verification.json').write_text(json.dumps({'variant':'centred-page','max_width_px':1600,'port':8775,'source':'work/consulting-contained-version','output':'outputs/consulting-contained-version','original_variant_separate':True},indent=2),encoding='utf8')
    print('Centred layout built independently at port 8775.')


if __name__ == '__main__':
    build()
