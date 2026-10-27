(function () {
  'use strict';
  const calculator = document.querySelector('#training-calculator');
  if (!calculator) return;
  const small = window.matchMedia('(max-width: 767px)');
  const cards = document.querySelectorAll('.course-details');
  function cardLayout() { cards.forEach(card => { card.open = !small.matches; }); }
  cardLayout();
  small.addEventListener('change', cardLayout);

  document.querySelectorAll('[data-choose-course]').forEach(button => button.addEventListener('click', () => {
    const row = calculator.querySelector('[data-course="' + button.dataset.chooseCourse + '"]');
    const checkbox = row.querySelector('.training-quote__checkbox');
    if (!checkbox.checked) { checkbox.checked = true; checkbox.dispatchEvent(new Event('change', {bubbles:true})); }
    row.scrollIntoView({behavior:'smooth', block:'center'});
    checkbox.focus({preventScroll:true});
  }));

  const bar = calculator.querySelector('[data-mobile-quote-bar]');
  const actions = calculator.querySelector('.training-quote__actions');
  let inCalculator = false, actionsVisible = false;
  function updateBar() {
    const active = document.activeElement;
    const editing = active && (active.tagName === 'SELECT' || active.tagName === 'TEXTAREA' || (active.tagName === 'INPUT' && !['checkbox','radio','button'].includes(active.type)));
    const count = calculator.querySelectorAll('.training-quote__checkbox:checked').length;
    bar.hidden = !small.matches || !inCalculator || actionsVisible || editing || !!document.querySelector('dialog[open]') || !count;
    bar.querySelector('[data-mobile-total]').textContent = calculator.querySelector('[data-quote-total]').textContent;
  }
  function updateFees() {
    calculator.querySelectorAll('[data-course]').forEach(row => {
      const show = row.querySelector('.training-quote__checkbox').checked && Number(row.querySelector('[data-days]').value) >= 5 && Number(row.querySelector('[data-participants]').value) < 3;
      row.querySelector('[data-minimum-fee]').hidden = !show;
    });
    updateBar();
  }
  calculator.addEventListener('change', updateFees);
  // Restore the exact saved cart on a browser Back navigation from checkout.
  document.addEventListener('click', event => {
    if (event.target.closest('[data-start-checkout]')) {
      try { sessionStorage.setItem('TE-usability-return', '1'); } catch (_) { /* Storage errors are handled by checkout. */ }
    }
  }, true);
  window.addEventListener('pageshow', () => {
    try {
      if (sessionStorage.getItem('TE-usability-return') === '1') {
        const cart = JSON.parse(sessionStorage.getItem('TE-training-cart-v1') || '{}');
        if (Array.isArray(cart.courses)) calculator.querySelectorAll('[data-course]').forEach(row => {
          const course = cart.courses.find(item => item.id === Number(row.dataset.course));
          row.querySelector('.training-quote__checkbox').checked = !!course;
          if (course) {
            row.querySelector('[data-days]').value = String(course.days);
            row.querySelector('[data-participants]').value = String(course.participants);
            row.querySelector('[data-start-date]').value = course.startDate || '';
          }
        });
        sessionStorage.removeItem('TE-usability-return');
      }
    } catch (_) { /* Keep the visible controls if session storage is unavailable. */ }
    calculator.dispatchEvent(new Event('change', {bubbles:true}));
  });
  document.addEventListener('focusin', updateBar);
  document.addEventListener('focusout', () => setTimeout(updateBar, 0));
  small.addEventListener('change', updateBar);
  bar.querySelector('[data-mobile-continue]').addEventListener('click', () => calculator.querySelector('[data-start-checkout]').click());
  new IntersectionObserver(entries => { inCalculator = entries[0].isIntersecting; updateBar(); }, {threshold:0}).observe(calculator);
  new IntersectionObserver(entries => { actionsVisible = entries[0].isIntersecting; updateBar(); }, {threshold:0}).observe(actions);
  document.querySelectorAll('dialog').forEach(dialog => new MutationObserver(updateBar).observe(dialog, {attributes:true, attributeFilter:['open']}));
  updateFees();

  const dialog = document.querySelector('#course-programme-dialog');
  document.querySelectorAll('[data-open-programme]').forEach(button => button.addEventListener('click', () => {
    dialog.querySelector('[data-programme-download]').href = '/training-order/api.php?action=course-programme&level=' + encodeURIComponent(button.dataset.openProgramme);
  }));
  dialog.querySelectorAll('[data-jump-part]').forEach(button => button.addEventListener('click', () => {
    const panel = dialog.querySelector('[data-dialogue-course]:not([hidden])');
    panel.querySelector('[data-parallel-day="' + button.dataset.jumpPart + '"]').scrollIntoView({behavior:'smooth',block:'start'});
  }));
})();
