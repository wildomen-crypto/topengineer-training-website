"""Course programmes in two parts, independent of the chosen training duration."""
from html import escape
import json
from programme_base import programmes, topic_count, sections_markup, PACING


def days_markup(course, prefix):
    days = []
    for day in course['days']:
        level, number = course['level'], day['day']
        count = sum(len(section['topics']) for section in day['sections'])
        heading_id = f'{prefix}-day-title-{level}-{number}'
        days.append(f'''<section class="parallel-day" id="{prefix}-day-panel-{level}-{number}" aria-labelledby="{heading_id}" data-parallel-day="{number}">
  <header class="parallel-day__header"><div><p class="parallel-day__number">Part {number}</p><h4 id="{heading_id}">{escape(day['label'])}</h4></div><p class="parallel-day__meta">{count} topics</p></header>
  {sections_markup(day)}
</section>''')
    return '<div class="parallel-days">' + ''.join(days) + '</div>'


def render_course_programmes():
    tabs, panels = [], []
    for course in programmes():
        level, selected = course['level'], course['level'] == 1
        title = escape(course['title'])
        tabs.append(f'<div class="col-6 col-lg-3" role="presentation"><button type="button" class="btn btn-outline-primary w-100 h-100 text-start{" active" if selected else ""}" role="tab" id="inline-course-tab-{level}" aria-controls="inline-course-panel-{level}" aria-selected="{str(selected).lower()}" aria-label="Level {level} programme" tabindex="{0 if selected else -1}"><span class="d-block fw-bold">Level {level}</span><span class="d-block small">{title}</span></button></div>')
        note = f'<p class="course-programme__section-note mb-3">{escape(course["note"])}</p>' if course.get('note') else ''
        panels.append(f'''<div role="tabpanel" id="inline-course-panel-{level}" aria-labelledby="inline-course-tab-{level}" data-inline-course-panel tabindex="0"{' hidden' if not selected else ''}>
  <div class="parallel-course-heading"><div><h3 class="h4 fw-bold mb-1">Level {level} · {title}</h3><p class="small text-muted mb-0">2 parts · {topic_count(course)} topics</p></div><button type="button" class="btn btn-outline-primary btn-sm" data-inline-expand>Collapse all topics</button></div>
  {note}{days_markup(course, 'inline')}
</div>''')
    return f'''<section id="course-programmes" class="row px-4 px-md-5 pb-5" aria-labelledby="course-programmes-title"><div class="container">
  <div class="section-title pt-4"><h2 id="course-programmes-title">Course programmes</h2><p>Explore each course in two parts. Select a section heading to expand or collapse its topics.</p></div>
  <div class="row g-3 mb-4" role="tablist" aria-label="Course programmes">{''.join(tabs)}</div>
  {''.join(panels)}<p class="small text-muted mt-3 mb-0">{PACING}</p>
  <noscript><p>Enable JavaScript to switch courses. Both parts of Level 1 are available below.</p></noscript>
</div></section>'''


def render_programme_dialog():
    courses = programmes()
    first = courses[0]
    panels = []
    metadata = []
    for course in courses:
        level = course['level']
        panels.append(f'<div data-dialogue-course="{level}"{' hidden' if level != 1 else ''}>{days_markup(course, "programme")}</div>')
        metadata.append({'level': level, 'title': course['title'], 'count': topic_count(course), 'note': course.get('note', '')})
    data = json.dumps(metadata, ensure_ascii=False).replace('<', '\\u003c')
    return f'''<dialog class="course-programme course-programme--parallel" id="course-programme-dialog" aria-labelledby="course-programme-title">
  <header class="course-programme__header"><div><p class="course-programme__eyebrow">FULL COURSE PROGRAMME</p><h2 id="course-programme-title">{escape(first['title'])}</h2><p class="course-programme__meta"><span data-programme-level>Level 1 · Basic course</span><span data-programme-summary>2 parts · {topic_count(first)} topics</span></p></div><button type="button" class="course-programme__close" data-close-programme aria-label="Close programme" autofocus><span>Close</span> <i class="bi bi-x-lg" aria-hidden="true"></i></button></header>
  <div class="course-programme__toolbar"><span>Both parts are shown below. Select a section heading to expand or collapse its topics.</span><button type="button" data-programme-expand>Collapse all sections</button></div>
  <div class="course-programme__scroll" data-programme-scroll><p class="course-programme__section-note mb-3" data-programme-note hidden></p>{''.join(panels)}<p class="course-programme__pacing">{PACING}</p></div>
  <footer class="course-programme__footer"><span>Choose your courses, dates and group size in the calculator.</span><button type="button" data-close-programme>Back to page</button></footer>
  <script type="application/json" data-programme-data>{data}</script>
</dialog>'''
