"""Build the independently deployable PHP B2B order module from the same course data."""
from pathlib import Path
from bs4 import BeautifulSoup
import hashlib,json,shutil

HERE=Path(__file__).resolve().parent


def build_checkout(output, html):
    source=HERE/'checkout-module'
    target=output/'training-order'
    shutil.copytree(source,target,dirs_exist_ok=True)
    shutil.copy2(source/'document-tools.js',output/'assets/document-tools.js')
    page=BeautifulSoup(html,'html.parser')
    data={
        'rates':json.loads(page.select_one('#training-rates').get_text()),
        'courses':json.loads((HERE/'course-programme.json').read_text(encoding='utf-8'))['courses'],
        'formats':json.loads((HERE/'training-formats.json').read_text(encoding='utf-8'))['formats'],
        'countries':json.loads((source/'data/countries.json').read_text(encoding='utf-8')),
        'agreementClauses':json.loads((source/'agreement-clauses.json').read_text(encoding='utf-8')),
        'bookProduct':json.loads((HERE/'book-product.json').read_text(encoding='utf-8')),
    }
    data['revision']=hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    (target/'data').mkdir(exist_ok=True)
    (target/'data/catalogue.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    (target/'data/.htaccess').write_text('Require all denied\n',encoding='utf-8')
    links=[str(link) for link in page.select('link[rel="stylesheet"]') if link['href'].startswith(('/bitrix/cache/css/','/vendor/fonts.googleapis.com/'))]
    checkout=(source/'index.html').read_text(encoding='utf-8').replace('<!-- SITE_STYLES -->','\n'.join(links))
    (target/'index.html').write_text(checkout,encoding='utf-8')
    (output/'Start-preview.ps1').write_text("$ProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))\n& (Join-Path $ProjectRoot 'tools/Start-Windows.ps1') @args\n",encoding='utf-8-sig')
