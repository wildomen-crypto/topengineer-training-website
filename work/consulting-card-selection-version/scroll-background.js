(function () {
  'use strict';
  const canvas = document.querySelector('body[data-scroll-background]');
  if (!canvas) return;

  // The introduction and course catalogue deliberately share the original white canvas.
  const palette = [
    ['.training-intro', '#ffffff'],
    ['#course-descriptions', '#ffffff'],
    ['#training-calculator', '#e9f2fb'],
    ['#how-training-works', '#edf6f2'],
    ['#training-books', '#faf1e5'],
    ['#training-formats', '#edf3fc'],
    ['#before-training', '#f0f3f6'],
    ['#course-certificate', '#faf5e9'],
    ['#after-training-support', '#eaf4ef'],
    ['#course-programmes', '#f1edf8'],
    ['#cta', '#ffffff'],
    ['#portfolio', '#ffffff'],
    ['#contact', '#ffffff']
  ];
  const sections = palette.map(([selector, colour]) => ({
    element: document.querySelector(selector),
    name: selector.replace(/^[.#]/, ''), colour, top: 0
  })).filter(section => section.element);
  if (!sections.length) return;

  let pending = false, needsMeasure = true, active = '';
  function update() {
    pending = false;
    if (needsMeasure) {
      const offset = window.scrollY;
      sections.forEach(section => {
        section.top = section.element.getBoundingClientRect().top + offset;
      });
      sections.sort((a, b) => a.top - b.top);
      needsMeasure = false;
    }
    // A new chapter takes over when its heading reaches the upper third of the viewport.
    const readingLine = window.scrollY + window.innerHeight * .35;
    let current = sections[0];
    for (const section of sections) {
      if (section.top > readingLine) break;
      current = section;
    }
    if (current.name === active) return;
    active = current.name;
    canvas.style.setProperty('--scroll-page-bg', current.colour);
    canvas.dataset.backgroundSection = current.name;
  }
  function schedule() {
    if (pending) return;
    pending = true;
    window.requestAnimationFrame(update);
  }
  function remeasure() { needsMeasure = true; schedule(); }

  window.addEventListener('scroll', schedule, {passive: true});
  window.addEventListener('resize', remeasure, {passive: true});
  window.addEventListener('pageshow', remeasure);
  window.addEventListener('hashchange', remeasure);
  window.addEventListener('load', remeasure, {once: true});
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) remeasure();
  });
  if ('ResizeObserver' in window) {
    const observer = new ResizeObserver(remeasure);
    sections.forEach(section => observer.observe(section.element));
  }
  if (document.fonts) document.fonts.ready.then(remeasure);
  update();
})();
