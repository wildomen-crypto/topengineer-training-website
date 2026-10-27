(function () {
  'use strict';
  const calculator = document.querySelector('#training-calculator');
  if (!calculator) return;
  const rates = JSON.parse(document.querySelector('#training-rates').textContent);
  const rows = Array.from(calculator.querySelectorAll('[data-course]'));
  const bookData = document.querySelector('#training-book-product');
  const bookProduct = bookData ? JSON.parse(bookData.textContent) : null;
  const bookRow = calculator.querySelector('[data-book-row]');
  const formatData = document.querySelector('#training-formats-data');
  const formats = new Map((formatData ? JSON.parse(formatData.textContent).formats : []).map(format => [format.days, format]));
  const currency = cents => new Intl.NumberFormat('en-IE', {style:'currency',currency:'EUR',minimumFractionDigits:2}).format(cents / 100);
  const plural = (number, word) => number + ' ' + word + (number === 1 ? '' : 's');
  const startCheckout = calculator.querySelector('[data-start-checkout]');
  const proposalButton = calculator.querySelector('[data-download-proposal]');
  let estimate;
  function cartPayload() {
    return {courses:estimate.courses.map(course => ({id:course.id,days:course.days,participants:course.participants,startDate:course.startDate || ''})),bookQuantity:estimate.bookQuantity};
  }

  function update() {
    const courses = rows.map(row => {
      const selected = row.querySelector('input[type="checkbox"]').checked;
      const duration = row.querySelector('[data-days]');
      const people = row.querySelector('[data-participants]');
      const start = row.querySelector('[data-start-date]');
      const end = row.querySelector('[data-end-date]');
      const endDate = CourseSchedule.endDate(start.value, Number(duration.value));
      const course = {id:Number(row.dataset.course),name:row.dataset.courseName,selected,days:Number(duration.value),participants:Number(people.value),startDate:start.value,endDate};
      const quote = CoursePricing.quote(course, rates);
      row.classList.toggle('is-selected', selected);
      duration.disabled = people.disabled = start.disabled = !selected;
      start.setCustomValidity(start.value && !endDate ? 'Choose an earlier start date so the course ends by 31 December 9999.' : '');
      end.textContent = selected && endDate ? CourseSchedule.formatDate(endDate) : '—';
      if (selected && endDate) end.dateTime = endDate;
      else end.removeAttribute('datetime');
      row.querySelector('[data-course-price]').textContent = selected ? currency(quote.totalCents) : '—';
      const format = formats.get(course.days);
      const formatLink = row.querySelector('[data-course-format]');
      if (formatLink && format) {
        formatLink.textContent = format.shortLabel;
        formatLink.title = format.enquiry;
        formatLink.setAttribute('aria-label', 'Compare training formats. Current selection: ' + format.enquiry);
      }
      return course;
    });
    estimate = CoursePricing.summarize(courses, rates);
    estimate.bookQuantity = 0;
    if (bookRow && bookProduct) {
      const selected = bookRow.querySelector('[data-book-selected]').checked;
      const quantity = bookRow.querySelector('[data-book-quantity]');
      const count = Number(quantity.value);
      if (!Number.isInteger(count) || count < 1 || count > bookProduct.maxQuantity) quantity.value = '1';
      estimate.bookQuantity = selected ? Number(quantity.value) : 0;
      estimate.bookTotalCents = estimate.bookQuantity * bookProduct.unitPriceCents;
      estimate.totalCents += estimate.bookTotalCents;
      quantity.disabled = !selected;
      bookRow.classList.toggle('is-selected', selected);
      bookRow.querySelector('[data-book-price]').textContent = selected ? currency(estimate.bookTotalCents) : '—';
    }
    const hasItems = estimate.courseCount > 0 || estimate.bookQuantity > 0;
    calculator.querySelector('[data-quote-total]').textContent = currency(estimate.totalCents);
    const meta = [];
    if (estimate.courseCount) meta.push(plural(estimate.courseCount, 'course'), plural(estimate.days, 'day'), plural(estimate.hours, 'hour'));
    if (estimate.bookQuantity) meta.push(plural(estimate.bookQuantity, 'book set'));
    calculator.querySelector('[data-total-meta]').textContent = hasItems ? meta.join(' · ') : 'Select a course or book set to see your estimate.';
    calculator.querySelector('[data-discuss-plan]').disabled = !hasItems;
    if (startCheckout) startCheckout.disabled = !hasItems;
    if (proposalButton) proposalButton.disabled = !hasItems || proposalButton.dataset.busy === 'true';
    calculator.querySelector('[data-clear-selection]').disabled = !hasItems;
  }
  calculator.addEventListener('change', event => {
    // Adding a course starts with the smallest group and duration. An existing
    // start date is retained; update() recalculates its end date and group fee.
    if (event.target.matches('[data-course] .training-quote__checkbox') && event.target.checked) {
      const row = event.target.closest('[data-course]');
      row.querySelector('[data-days]').value = '2';
      row.querySelector('[data-participants]').value = '1';
    }
    update();
  });
  calculator.addEventListener('input', event => {
    if (event.target.matches('[data-start-date]')) update();
  });
  calculator.querySelector('[data-clear-selection]').addEventListener('click', () => {
    rows.forEach(row => { row.querySelector('input[type="checkbox"]').checked = false; });
    if (bookRow) bookRow.querySelector('[data-book-selected]').checked = false;
    update();
  });

  const priceDialog = document.querySelector('#course-price-table');
  const tabs = Array.from(priceDialog.querySelectorAll('[data-price-tab]'));
  function activate(tab, focus) {
    tabs.forEach(item => {
      const selected = item === tab;
      item.setAttribute('aria-selected', String(selected));
      item.tabIndex = selected ? 0 : -1;
      document.querySelector('#' + item.getAttribute('aria-controls')).hidden = !selected;
    });
    if (focus) tab.focus();
  }
  calculator.querySelector('[data-open-price-table]').addEventListener('click', () => priceDialog.showModal());
  priceDialog.querySelector('[data-close-price-table]').addEventListener('click', () => priceDialog.close());
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activate(tab, false));
    tab.addEventListener('keydown', event => {
      let target;
      if (event.key === 'ArrowRight') target = (index + 1) % tabs.length;
      else if (event.key === 'ArrowLeft') target = (index + tabs.length - 1) % tabs.length;
      else if (event.key === 'Home') target = 0;
      else if (event.key === 'End') target = tabs.length - 1;
      else return;
      event.preventDefault();
      activate(tabs[target], true);
    });
  });

  const planDialog = document.querySelector('#training-plan-dialog');
  const summary = planDialog.querySelector('textarea');
  calculator.querySelector('[data-discuss-plan]').addEventListener('click', () => {
    if (!estimate.courseCount && !estimate.bookQuantity) return;
    const lines = ['Tekla Structures training enquiry', ''];
    estimate.courses.forEach(course => {
      lines.push('Level ' + course.id + ': ' + course.name, plural(course.days, 'day') + ' / ' + plural(course.hours, 'hour') + ' (8 hours per day)', plural(course.participants, 'participant') + (course.billedParticipants > course.participants ? ' — minimum fee for ' + course.billedParticipants : ''), 'Desired start date: ' + (CourseSchedule.formatDate(course.startDate) || 'To be agreed'), 'Calculated end date: ' + (CourseSchedule.formatDate(course.endDate) || 'To be agreed'), 'Group price: ' + currency(course.totalCents), '');
      const format = formats.get(course.days);
      if (format) lines.splice(lines.length - 1, 0, 'Training format: ' + format.enquiry);
    });
    if (estimate.bookQuantity) lines.push(bookProduct.name, bookProduct.description, plural(estimate.bookQuantity, 'set') + ' × ' + currency(bookProduct.unitPriceCents) + ' = ' + currency(estimate.bookTotalCents), '');
    lines.push('Total for selected items: ' + currency(estimate.totalCents));
    if (estimate.courseCount) lines.push(plural(estimate.days, 'day') + ' / ' + plural(estimate.hours, 'hour'), '', 'End dates count all calendar days, including the start date. Dates are provisional, subject to confirmation with the tutor.');
    lines.push('', 'I would like to ask about this order.');
    summary.value = lines.join('\n');
    planDialog.querySelector('[data-email-plan]').href = 'mailto:info@top-engineer.com?subject=' + encodeURIComponent('Tekla Structures training plan') + '&body=' + encodeURIComponent(summary.value);
    planDialog.querySelector('[data-copy-status]').textContent = '';
    planDialog.showModal();
  });
  planDialog.querySelector('[data-close-plan]').addEventListener('click', () => planDialog.close());
  planDialog.querySelector('[data-copy-plan]').addEventListener('click', async () => {
    const status = planDialog.querySelector('[data-copy-status]');
    try {
      await navigator.clipboard.writeText(summary.value);
      status.textContent = 'Your training plan has been copied.';
    } catch {
      summary.focus();
      summary.select();
      status.textContent = 'The plan is selected. Copy it using your keyboard or device menu.';
    }
  });
  if (startCheckout) startCheckout.addEventListener('click', () => {
    if (!estimate || (!estimate.courseCount && !estimate.bookQuantity)) return;
    try {
      sessionStorage.setItem('TE-training-cart-v1', JSON.stringify(cartPayload()));
      location.href = new URL('./training-order/', location.href).href;
    } catch {
      const message = document.getElementById('checkout-cart-error');
      message.textContent = 'Your browser could not save the selected courses for checkout. Please allow session storage and try again.';
      message.hidden = false;
    }
  });
  if (proposalButton) proposalButton.addEventListener('click', async () => {
    if (!estimate || (!estimate.courseCount && !estimate.bookQuantity) || proposalButton.dataset.busy === 'true') return;
    const message = document.getElementById('checkout-cart-error');
    message.hidden = true;
    const cart = cartPayload();
    try {
      await TrainingDocuments.downloadProposal(new URL('./training-order/api.php',location.href).href,cart.courses,TrainingDocuments.readCustomer(),proposalButton,document.getElementById('proposal-download-status'),cart.bookQuantity);
    } catch (failure) {
      message.textContent = failure.message || 'The proposal could not be downloaded. Please try again.';
      message.hidden = false;
    } finally { update(); }
  });
  if (new URLSearchParams(location.search).get('editOrder') === '1') {
    try {
      const cart = JSON.parse(sessionStorage.getItem('TE-training-cart-v1'));
      if (cart && Array.isArray(cart.courses) && cart.courses.every(c => Number.isInteger(c.id) && c.id >= 1 && c.id <= 4 && [2,5,10].includes(c.days) && Number.isInteger(c.participants) && c.participants >= 1 && c.participants <= 20)) {
        rows.forEach(row => {
          const course = cart.courses.find(c => c.id === Number(row.dataset.course));
          row.querySelector('input[type="checkbox"]').checked = !!course;
          if (course) {
            row.querySelector('[data-days]').value = String(course.days);
            row.querySelector('[data-participants]').value = String(course.participants);
            row.querySelector('[data-start-date]').value = course.startDate || '';
          }
        });
        if (bookRow && Number.isInteger(cart.bookQuantity) && cart.bookQuantity >= 0 && cart.bookQuantity <= bookProduct.maxQuantity) {
          bookRow.querySelector('[data-book-selected]').checked = cart.bookQuantity > 0;
          bookRow.querySelector('[data-book-quantity]').value = String(cart.bookQuantity || 1);
        }
      }
    } catch { /* A new visit keeps the existing Level 1 / one-person defaults. */ }
  }
  document.querySelectorAll('[data-add-book-set]').forEach(button => button.addEventListener('click', () => {
    if (!bookRow) return;
    const checkbox = bookRow.querySelector('[data-book-selected]');
    checkbox.checked = true;
    checkbox.dispatchEvent(new Event('change', {bubbles:true}));
    bookRow.scrollIntoView({behavior:'smooth',block:'center'});
    checkbox.focus({preventScroll:true});
  }));
  update();
})();
