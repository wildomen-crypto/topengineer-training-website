"""Build a separate full-width site with three interactive lesson views."""
from pathlib import Path
import importlib.util
import json
import shutil
from bs4 import BeautifulSoup
import build_card_selection
import build_parallel

HERE=Path(__file__).resolve().parent
OUT=build_parallel.OUT
spec=importlib.util.spec_from_file_location('lesson_demo',HERE/'lesson-demo.py')
demo=importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


def build():
    build_card_selection.build()
    page=BeautifulSoup((OUT/'index.html').read_text(encoding='utf8'),'html.parser')
    section=page.select_one('#how-training-works')
    column=section.select_one('.training-process__media').parent
    column['class']=['col-lg-6','lesson-demo-column']
    column.clear()
    column.append(BeautifulSoup(demo.markup(),'html.parser'))
    copy=section.select_one('.col-lg-7')
    copy['class']=['col-lg-6','lesson-demo-copy']
    item=copy.select('ol > li')[2]
    item.h3.string='3. Watch, work and get feedback'
    item.p.string='You use one monitor to follow your instructor and the other to work in Tekla. Your instructor shares their own model and follows your shared screen on a second monitor.'
    page.head.append(BeautifulSoup('<link rel="stylesheet" href="/assets/lesson-demo.css?v=3">','html.parser'))
    page.body.append(BeautifulSoup('<script src="/assets/lesson-demo.js?v=3" defer></script>','html.parser'))
    (OUT/'index.html').write_text(str(page),encoding='utf8')
    for name in ['lesson-demo.css','lesson-demo.js']: shutil.copy2(HERE/name,OUT/'assets'/name)
    (OUT/'Start-preview.ps1').write_text("$ProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))\n& (Join-Path $ProjectRoot 'tools/Start-Interactive-Lesson.ps1') @args\n",encoding='utf-8-sig')
    (OUT/'README.txt').write_text('Independent interactive-lesson version. Preview: http://127.0.0.1:8776/#how-training-works. Run tools/Start-Interactive-Lesson.ps1 from the repository root. Source: work/consulting-interactive-lesson. Build: python -X utf8 work/consulting-interactive-lesson/build_interactive.py.\n',encoding='utf8')
    (OUT/'qa/source-verification.json').write_text(json.dumps({'variant':'interactive-lesson','port':8776,'views':['map','steps','perspective'],'other_sections_preserved':True,'original_version_separate':True},indent=2),encoding='utf8')
    print('Interactive lesson version built independently at port 8776.')


if __name__=='__main__': build()
