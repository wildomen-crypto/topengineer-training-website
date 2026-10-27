(function (root, factory) {
  const schedule = factory();
  if (typeof module === 'object' && module.exports) module.exports = schedule;
  else root.CourseSchedule = schedule;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  function parseDate(value) {
    if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return null;
    const [year, month, day] = value.split('-').map(Number);
    if (year < 1) return null;
    // UTC date-only arithmetic keeps the calendar stable across time zones and DST.
    const date = new Date(0);
    date.setUTCFullYear(year, month - 1, day);
    if (date.getUTCFullYear() !== year || date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day) return null;
    return date;
  }

  function endDate(start, days) {
    const date = parseDate(start);
    if (!date || !Number.isInteger(days) || days < 1) return '';
    // The start date is the first training day; weekends are included.
    date.setUTCDate(date.getUTCDate() + days - 1);
    if (!Number.isFinite(date.getTime()) || date.getUTCFullYear() > 9999) return '';
    return date.toISOString().slice(0, 10);
  }

  function formatDate(value) {
    const date = parseDate(value);
    return date ? new Intl.DateTimeFormat('en-GB', {day:'numeric',month:'short',year:'numeric',timeZone:'UTC'}).format(date) : '';
  }

  return {endDate, formatDate};
});
