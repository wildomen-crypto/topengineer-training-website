(function () {
  'use strict';
  const dialog = document.querySelector('#course-programme-dialog');
  if (!dialog) return;
  const scrollArea = dialog.querySelector('[data-programme-scroll]');
  const expandButton = dialog.querySelector('[data-programme-expand]');
  const courses = JSON.parse(dialog.querySelector('[data-programme-data]').textContent);
  let previousOverflow = '';

  function activeSections() {
    return Array.from(dialog.querySelector('[data-dialogue-course]:not([hidden])').querySelectorAll('details'));
  }
  function updateExpandButton() {
    expandButton.textContent = activeSections().every(section => section.open) ? 'Collapse all sections' : 'Expand all sections';
  }
  document.querySelectorAll('[data-open-programme]').forEach(button => {
    button.addEventListener('click', () => {
      const level = Number(button.dataset.openProgramme);
      const course = courses.find(item => item.level === level);
      if (!course) return;
      dialog.querySelector('#course-programme-title').textContent = course.title;
      dialog.querySelector('[data-programme-level]').textContent = 'Level ' + level + (level === 1 ? ' · Basic course' : ' · Advanced course');
      dialog.querySelector('[data-programme-summary]').textContent = '2 parts · ' + course.count + ' topics';
      const notice = dialog.querySelector('[data-programme-note]');
      notice.hidden = !course.note;
      notice.textContent = course.note;
      dialog.querySelectorAll('[data-dialogue-course]').forEach(panel => {
        panel.hidden = Number(panel.dataset.dialogueCourse) !== level;
        if (!panel.hidden) panel.querySelectorAll('details').forEach(section => { section.open = true; });
      });
      updateExpandButton();
      previousOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      dialog.showModal();
      scrollArea.scrollTop = 0;
    });
  });
  dialog.querySelectorAll('[data-close-programme]').forEach(button => button.addEventListener('click', () => dialog.close()));
  dialog.addEventListener('close', () => { document.body.style.overflow = previousOverflow; });
  dialog.addEventListener('toggle', event => {
    if (event.target.tagName === 'DETAILS') updateExpandButton();
  }, true);
  expandButton.addEventListener('click', () => {
    const sections = activeSections();
    const open = !sections.every(section => section.open);
    sections.forEach(section => { section.open = open; });
    updateExpandButton();
  });
})();
