"""Render the four real curricula using the existing Bootstrap/programme styles."""
from pathlib import Path
from html import escape
import json

HERE = Path(__file__).resolve().parent
PACING = 'Each course programme is organised into two parts. The teaching schedule and time for practical exercises are agreed with your instructor to suit your chosen course duration.'

def programmes():
    return json.loads((HERE / 'course-programme.json').read_text(encoding='utf-8'))['courses']

def topic_count(course):
    return sum(len(section['topics']) for day in course['days'] for section in day['sections'])

def sections_markup(day, numbered=False):
    result = []
    for number, section in enumerate(day['sections'], 1):
        topics = ''.join(f'<li><span class="course-programme__topic-code">{escape(code)}</span><span>{escape(title)}</span></li>' for code, title in section['topics'])
        note = f'<p class="course-programme__section-note">{escape(section["note"])}</p>' if section.get('note') else ''
        badge = f'<span class="course-programme__section-number" aria-hidden="true">{number:02}</span>' if numbered else ''
        result.append(f'<details class="course-programme__section" open><summary>{badge}<span><strong>{escape(section["title"])}</strong><small>{len(section["topics"])} topics</small></span><i class="bi bi-chevron-down" aria-hidden="true"></i></summary><div class="course-programme__section-content">{note}<ol role="list">{topics}</ol></div></details>')
    return ''.join(result)

def render_course_programmes(titles):
    tabs, panels = [], []
    for course, title in zip(programmes(), titles):
        level, selected = course['level'], course['level'] == 1
        tabs.append(f'<div class="col-6 col-lg-3" role="presentation"><button type="button" class="btn btn-outline-primary w-100 h-100 text-start{" active" if selected else ""}" role="tab" id="inline-course-tab-{level}" aria-controls="inline-course-panel-{level}" aria-selected="{str(selected).lower()}" aria-label="Level {level} programme" tabindex="{0 if selected else -1}"><span class="d-block fw-bold">Level {level}</span><span class="d-block small">{escape(title)}</span></button></div>')
        day_tabs, day_panels = [], []
        for day in course['days']:
            number, first = day['day'], day['day'] == 1
            count = sum(len(section['topics']) for section in day['sections'])
            day_tabs.append(f'<button type="button" class="btn btn-outline-primary{" active" if first else ""}" role="tab" id="inline-day-tab-{level}-{number}" aria-controls="inline-day-panel-{level}-{number}" aria-selected="{str(first).lower()}" aria-label="Day {number} for Level {level}" tabindex="{0 if first else -1}">Day {number} · {escape(day["label"])}<span class="d-block small">8 hours · {count} topics</span></button>')
            day_panels.append(f'<div role="tabpanel" id="inline-day-panel-{level}-{number}" aria-labelledby="inline-day-tab-{level}-{number}" data-inline-day-panel tabindex="0"{" hidden" if not first else ""}>{sections_markup(day)}</div>')
        note = f'<p class="small text-muted mb-3">{escape(course["note"])}</p>' if course.get('note') else ''
        panels.append(f'<div role="tabpanel" id="inline-course-panel-{level}" aria-labelledby="inline-course-tab-{level}" data-inline-course-panel tabindex="0"{" hidden" if not selected else ""}><h3 class="h4 fw-bold mb-2">Level {level} · {escape(title)}</h3><p class="small text-muted mb-3">2-day outline · 16 teaching hours · {topic_count(course)} topics</p>{note}<div class="d-flex flex-wrap gap-2 mb-3" role="tablist" aria-label="Days for Level {level}">{"".join(day_tabs)}</div><div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3"><p class="small text-muted mb-0">Select a section heading to expand or collapse its topics.</p><button type="button" class="btn btn-outline-primary btn-sm" data-inline-expand>Collapse all topics</button></div>{"".join(day_panels)}</div>')
    return f'<section id="course-programmes" class="row px-4 px-md-5 pb-5" aria-labelledby="course-programmes-title"><div class="container"><div class="section-title pt-4"><h2 id="course-programmes-title">Course programmes</h2><p>Choose a course and explore the topics day by day.</p></div><div class="row g-3 mb-4" role="tablist" aria-label="Course programmes">{"".join(tabs)}</div>{"".join(panels)}<p class="small text-muted mt-3 mb-0">{PACING}</p><noscript><p>Enable JavaScript to switch courses and days. The Level 1 Day 1 programme is available on this page.</p></noscript></div></section>'

def render_programme_dialog():
    courses = programmes()
    first = courses[0]
    tabs, panels = [], []
    metadata = []
    for day in first['days']:
        number = day['day']
        count = sum(len(section['topics']) for section in day['sections'])
        tabs.append(f'<button type="button" role="tab" id="programme-tab-{number}" data-programme-tab="{number}" aria-controls="programme-day-1-{number}" aria-selected="{str(number == 1).lower()}" tabindex="{0 if number == 1 else -1}"><strong data-programme-day-label>Day {number} · {escape(day["label"])}</strong><span data-programme-day-count>{count} topics</span></button>')
    for course in courses:
        metadata.append({'level': course['level'], 'title': course['title'], 'count': topic_count(course), 'note': course.get('note', ''), 'days': [{'day': day['day'], 'label': day['label'], 'count': sum(len(section['topics']) for section in day['sections'])} for day in course['days']]})
        for day in course['days']:
            level, number = course['level'], day['day']
            visible = level == 1 and number == 1
            panels.append(f'<div role="tabpanel" id="programme-day-{level}-{number}" aria-labelledby="programme-tab-{number}" data-dialogue-course="{level}" data-dialogue-day="{number}" tabindex="0"{" hidden" if not visible else ""}>{sections_markup(day, numbered=True)}</div>')
    data = json.dumps(metadata, ensure_ascii=False).replace('<', '\\u003c')
    return f'''<dialog class="course-programme" id="course-programme-dialog" aria-labelledby="course-programme-title">
  <header class="course-programme__header"><div><p class="course-programme__eyebrow">FULL COURSE PROGRAMME</p><h2 id="course-programme-title">{escape(first['title'])}</h2><p class="course-programme__meta"><span data-programme-level>Level 1 · Basic course</span><span data-programme-summary>2-day outline · 16 teaching hours · {topic_count(first)} topics</span></p></div><button type="button" class="course-programme__close" data-close-programme aria-label="Close programme" autofocus><span>Close</span> <i class="bi bi-x-lg" aria-hidden="true"></i></button></header>
  <div class="course-programme__tabs" role="tablist" aria-label="Course programme days">{''.join(tabs)}</div>
  <div class="course-programme__toolbar"><span>Explore the topics in each section</span><button type="button" data-programme-expand>Collapse all sections</button></div>
  <div class="course-programme__scroll" data-programme-scroll><p class="course-programme__section-note" data-programme-note hidden></p>{''.join(panels)}<p class="course-programme__pacing">{PACING}</p></div>
  <footer class="course-programme__footer"><span>Choose your courses, dates and group size in the calculator.</span><button type="button" data-close-programme>Back to page</button></footer>
  <script type="application/json" data-programme-data>{data}</script>
</dialog>'''
