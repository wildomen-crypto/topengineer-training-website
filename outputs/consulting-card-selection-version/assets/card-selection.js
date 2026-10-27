(function () {
  'use strict';
  const calculator = document.querySelector('#training-calculator');
  if (!calculator) return;
  const cards = Array.from(document.querySelectorAll('[data-selectable-card]'));
  function syncCards() {
    cards.forEach(card => {
      const level = card.dataset.selectableCard;
      const selected = calculator.querySelector('[data-course="' + level + '"] .training-quote__checkbox').checked;
      card.classList.toggle('course-card-selected', selected);
      card.querySelector('[data-card-choice]').checked = selected;
      card.querySelector('[data-card-choice-label]').textContent = selected ? 'Selected' : 'Select course';
    });
  }
  function setCourse(card, selected) {
    const checkbox = calculator.querySelector('[data-course="' + card.dataset.selectableCard + '"] .training-quote__checkbox');
    if (checkbox.checked !== selected) {
      checkbox.checked = selected;
      checkbox.dispatchEvent(new Event('change', {bubbles:true}));
    } else syncCards();
  }
  cards.forEach(card => {
    const checkbox = card.querySelector('[data-card-choice]');
    checkbox.addEventListener('change', () => setCourse(card, checkbox.checked));
    card.addEventListener('click', event => {
      if (event.target.closest('a, button, input, label, summary, select, textarea')) return;
      if (window.getSelection && String(window.getSelection()).length) return;
      setCourse(card, !checkbox.checked);
    });
  });
  calculator.addEventListener('change', syncCards);
  window.addEventListener('pageshow', syncCards);
  syncCards();
})();
