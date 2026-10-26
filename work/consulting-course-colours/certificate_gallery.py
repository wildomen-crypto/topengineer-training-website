"""Certificate artwork stays separate so sheets can overlap as space decreases."""
import re


CERTIFICATES = (
    (2, 16, 'Essentials', 'essential training', 'blue', 'TE-SAMPLE-002'),
    (5, 40, 'In-depth training', 'in-depth training', 'teal', 'TE-SAMPLE-005'),
    (10, 80, 'Training + your pilot project', 'training and work on your own pilot project', 'bronze', 'TE-SAMPLE-010'),
)


def render_certificate_section():
    sheets = []
    links = []
    types = []
    for index, (days, hours, label, description, colour, number) in enumerate(CERTIFICATES):
        asset = f'/assets/topengineer-certificate-{days}-days.png'
        accessible = f'View the {days}-day certificate sample in full size'
        sheets.append(f'''<a class="certificate-sheet certificate-{colour} portfolio-lightbox" data-gallery="certificateGallery" style="--sheet-index:{index}" href="{asset}" aria-label="{accessible}">
<img src="{asset.replace('.png', '.webp')}" width="1536" height="1024" loading="lazy" decoding="async" alt="Sample personalised TopEngineer certificate for {days} days and {hours} hours of {description}, with unique number {number}.">
</a>''')
        # Separate entry-point groups keep each certificate from appearing twice.
        links.append(f'''<a class="certificate-duration certificate-{colour} portfolio-lightbox" data-gallery="certificateDurationGallery" href="{asset}" aria-label="{accessible}"><strong>{days} days</strong><span>{hours} hours · View</span></a>''')
        types.append(f'''<li class="certificate-type certificate-{colour}"><h3 class="h6 fw-bold mb-1">{days} days · {hours} hours</h3><p class="mb-0">{label}</p></li>''')
    return f'''<section aria-labelledby="course-certificate-title" class="row px-4 px-md-5 pb-5" id="course-certificate">
<div class="container">
<div class="section-title pt-4">
<h2 id="course-certificate-title">Your certificate of completion</h2>
<p>Three certificate types to reflect the duration of your completed training.</p>
</div>
<div class="certificate-layout">
<figure class="certificate-gallery mb-0" aria-describedby="certificate-samples-note">
<div class="certificate-deck">{''.join(sheets)}</div>
<div class="certificate-durations">{''.join(links)}</div>
<figcaption class="small text-muted text-center mt-3" id="certificate-samples-note">Sample certificates. Select a sheet or duration to view full size.</figcaption>
</figure>
<div class="certificate-copy">
<p>After completing your course, each participant receives a personalised digital certificate issued by TopEngineer. We offer three types, based on your training duration:</p>
<ul class="certificate-types list-unstyled">{''.join(types)}</ul>
<p class="mb-0">Your certificate records the course completed and your name, and has a unique certificate number. Keep the electronic version or print your own paper copy.</p>
</div>
</div>
</div>
</section>'''


def replace_certificate_section(html):
    html, count = re.subn(r'<section\b(?=[^>]*\bid="course-certificate")[^>]*>.*?</section>', lambda _: render_certificate_section(), html, count=1, flags=re.S)
    assert count == 1, 'The certificate section must be replaced exactly once'
    return html
