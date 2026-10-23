"""Keep the initial quote small and give each course a consistent numbered label."""
from bs4 import BeautifulSoup
from training_formats import format_data


def level_badge(soup, level):
    badge = soup.new_tag('span', attrs={'class': 'course-level', 'data-level': str(level)})
    badge.string = f'Level {level}'
    return badge


def calculator_markup(markup):
    soup = BeautifulSoup(markup, 'html.parser')
    initial_format = format_data()['formats'][0]
    for row in soup.select('[data-course]'):
        level = int(row['data-course'])
        selected = level == 1
        row['class'] = ['training-quote__course'] + (['is-selected'] if selected else [])
        checkbox = row.select_one('input[type="checkbox"]')
        checkbox.attrs.pop('checked', None)
        if selected:
            checkbox['checked'] = ''
        for selector, default in [('[data-days]', '2'), ('[data-participants]', '1')]:
            control = row.select_one(selector)
            control.attrs.pop('disabled', None)
            if not selected:
                control['disabled'] = ''
            for option in control.select('option'):
                option.attrs.pop('selected', None)
                if option['value'] == default:
                    option['selected'] = ''
        start = row.select_one('[data-start-date]')
        start.attrs.pop('value', None)
        start.attrs.pop('disabled', None)
        if not selected:
            start['disabled'] = ''
        row.select_one('[data-course-price]').string = '€450.00' if selected else '—'
        title = row.select_one('.training-quote__title')
        title.insert_before(level_badge(soup, level))
        format_link = soup.new_tag('a', attrs={
            'href': '#training-formats',
            'class': 'training-quote__format-link',
            'data-course-format': '',
            'title': initial_format['enquiry'],
            'aria-label': 'Compare training formats. Current selection: ' + initial_format['enquiry'],
        })
        format_link.string = initial_format['shortLabel']
        programme = row.select_one('.training-quote__programme-link')
        programme.insert_after(format_link)
        programme.insert_after(soup.new_string(' '))
    soup.select_one('[data-quote-total]').string = '€450.00'
    soup.select_one('[data-total-meta]').string = '1 course · 2 days · 16 hours'
    actions = soup.select_one('.training-quote__actions')
    question = actions.select_one('[data-discuss-plan]')
    question['class'] = ['btn', 'btn-outline-primary']
    question.clear()
    question.string = 'Ask a question'
    buttons = soup.new_tag('div', attrs={'class': 'd-flex flex-wrap gap-2 justify-content-end'})
    question.replace_with(buttons)
    checkout = soup.new_tag('button', attrs={'type': 'button', 'class': 'training-quote__discuss', 'data-start-checkout': ''})
    checkout.string = 'Get proposal & invoice'
    buttons.append(question)
    buttons.append(checkout)
    error = soup.new_tag('p', attrs={'id': 'checkout-cart-error', 'class': 'small text-danger mt-2', 'role': 'alert', 'hidden': ''})
    actions.insert_after(error)
    return str(soup)


def description_markup(markup, level):
    soup = BeautifulSoup(markup, 'html.parser')
    heading = soup.select_one(f'#original-course-level-{level}-title')
    # Preserve the hidden course title used by screen readers.
    for child in list(heading.contents):
        if isinstance(child, str):
            child.extract()
    heading.insert(0, level_badge(soup, level))
    return str(soup)


def programme_tabs_markup(markup):
    soup = BeautifulSoup(markup, 'html.parser')
    for level in range(1, 5):
        caption = soup.select_one(f'#inline-course-tab-{level} > span')
        caption.clear()
        caption.append(level_badge(soup, level))
    return str(soup)
