(function (root, factory) {
  const pricing = factory();
  if (typeof module === 'object' && module.exports) module.exports = pricing;
  else root.CoursePricing = pricing;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  function quote(course, rates) {
    const days = Number(course.days);
    const participants = Number(course.participants);
    if (!rates.days.includes(days) || !Number.isInteger(participants) || participants < 1 || participants > rates.maxParticipants) {
      throw new RangeError('Choose a listed duration and a valid whole number of participants.');
    }
    const billedParticipants = Math.max(participants, rates.minimumBillableParticipants[String(days)] || 1);
    const price = rates.totalsCents[String(days)]?.[String(billedParticipants)];
    return {
      ...course,
      days,
      participants,
      billedParticipants,
      hours: days * rates.hoursPerDay,
      totalCents: Number.isInteger(price) && price >= 0 ? price : null
    };
  }

  function summarize(courses, rates) {
    const selected = courses.filter(course => course.selected).map(course => quote(course, rates));
    const knownSubtotalCents = selected.reduce((total, course) => total + (course.totalCents ?? 0), 0);
    const unpricedCount = selected.filter(course => course.totalCents === null).length;
    return {
      courses: selected,
      courseCount: selected.length,
      days: selected.reduce((total, course) => total + course.days, 0),
      hours: selected.reduce((total, course) => total + course.hours, 0),
      knownSubtotalCents,
      unpricedCount,
      totalCents: unpricedCount ? null : knownSubtotalCents
    };
  }

  return { quote, summarize };
});
