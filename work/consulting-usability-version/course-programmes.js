(function () {
  'use strict';
  const root = document.querySelector('#course-programmes');
  if (!root) return;
  const tablist = root.querySelector('[role="tablist"]');
  const tabs = Array.from(tablist.querySelectorAll('[role="tab"]'));
  const panels = Array.from(root.querySelectorAll('[data-inline-course-panel]'));

  // Both day sections belong to the selected course: neither day is hidden.
  function sectionsFor(panel) {
    return Array.from(panel.querySelectorAll('[data-parallel-day] details'));
  }
  function updateExpandButton(panel) {
    panel.querySelector('[data-inline-expand]').textContent = sectionsFor(panel).every(section => section.open) ? 'Collapse all topics' : 'Expand all topics';
  }
  function activate(tab, focus) {
    tabs.forEach(item => {
      const selected = item === tab;
      item.setAttribute('aria-selected', String(selected));
      item.tabIndex = selected ? 0 : -1;
      item.classList.toggle('active', selected);
      root.querySelector('#' + item.getAttribute('aria-controls')).hidden = !selected;
    });
    if (focus) tab.focus();
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activate(tab, false));
    tab.addEventListener('keydown', event => {
      if (event.ctrlKey || event.metaKey || event.altKey) return;
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      else if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
      else if (event.key === 'Home') next = 0;
      else if (event.key === 'End') next = tabs.length - 1;
      else return;
      event.preventDefault();
      activate(tabs[next], true);
    });
  });
  panels.forEach(panel => {
    panel.querySelector('[data-inline-expand]').addEventListener('click', () => {
      const sections = sectionsFor(panel);
      const open = !sections.every(section => section.open);
      sections.forEach(section => { section.open = open; });
      updateExpandButton(panel);
    });
    panel.addEventListener('toggle', event => {
      if (event.target.tagName === 'DETAILS') updateExpandButton(panel);
    }, true);
  });
})();
