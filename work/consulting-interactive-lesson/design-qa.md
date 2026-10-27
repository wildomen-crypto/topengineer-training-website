# Interactive lesson: design QA

final result: passed

Scope: the separate full-width page on port 8776. The original selectable-card page on 8774 and the centred alternative on 8775 remain independent.

## Visual review

Reviewed the supplied original screenshot and screenshots of all three rendered modes together in one comparison image. The blue centred heading, subtitle, original typefaces and Bootstrap styling remain. Intentional differences are the interactive panel, an equal-width pair of columns and the revised explanation of two-way sharing in step 3. No other section was redesigned.

The widget uses a real TopEngineer project render. It does not pretend to be a live Tekla application. SVG paths connect the measured endpoints of the actual screen buttons and update when those buttons move.

## Checks

- Desktop widths: 2560, 1920, 1536, 1366 and 1024 px. Both columns have equal heights; the flexible middle area increases from 40 px at 1920 to approximately 74 px at 1024. The matching cable endpoints stay aligned after resizing.
- Tablet / phone widths: 768, 390 and 320 px. The widget stacks above the explanatory text, controls wrap, all labels remain visible, and there is no horizontal page overflow.
- Inspected the two additional modes at 390 px. No overflowing button text or clipped controls.
- All three tabs work; arrow keys and Home / End navigate the tabs. Selected state, controlled panel IDs and keyboard focus indicators are provided.
- Selecting a screen highlights the corresponding instructor or participant feed. A/B labels identify feeds independently of colour.
- Watch, Practise and Review work, including Previous / Next and disabled first / last navigation states.
- The perspective switch updates both screen labels and the desk explanation.
- Play starts automatic progression; an observation during playback confirmed progression from the demonstration to the joint review. Pause stops it. Playback also stops when the component leaves the viewport or the page is hidden. Reduced-motion settings disable cable animation.
- Default calculator quote remains one Level 1 course, 2 days, 1 participant, EUR 450. Adding one electronic book set produces EUR 539. Both items and the total transfer correctly to checkout. The test selection was restored afterwards.
- SHA-256 verification: the original source and output files remain unchanged. The copied order backend and PDF sources are byte-identical. Course descriptions, calculator, books, formats, preparation, certificates, support and all 352 programme topics remain unchanged outside the intended training-workflow section.
- The new server generated a one-page proposal containing all four courses plus one book set (EUR 1,889). Verified all 680 checkout / PDF files against the original. The public PDF parser's Settings.php class is explicitly retained despite the general private-settings ignore rule.
- New JavaScript passes the syntax check. No errors were recorded for lesson-demo.js. The copied site's existing navbar script still reports an invalid #bim-modeling/ selector on scrolling; that unrelated vendor issue is outside this change.

Screenshots and transient verification data are stored outside version control. No customer records, private banking settings or generated customer documents are included. Payment mode is unchanged (PREVIEW).
