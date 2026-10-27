# Interactive lesson explanation

Independent copy of the original full-width page. The image in **How the training works** is replaced with three working explanations of two-way screen sharing:

1. **Two-way view:** two workstations, each with two monitors. Select a screen to highlight its shared counterpart. The responsive cable paths connect the matching feeds.
2. **Step by step:** watch, practise and review, with working step buttons and previous/next controls.
3. **My view:** switch between the participant's and instructor's monitors.

Play/pause controls cycle through the three teaching stages. Playback stops outside the viewport or when the page is hidden. Reduced-motion preferences disable cable animation.

The workspace rows are separated by a flexible sharing area. When the adjacent text becomes taller, that area grows and the cable endpoints are recalculated with ResizeObserver. On mobile the component takes its own natural height above the text.

The previews use an existing TopEngineer project render, not a fabricated Tekla interface. The paths are functional connections between measured screen endpoints. The demonstration is illustrative; it is not a live call or a CAD editor.

- Run `Start-Interactive-Lesson.cmd` from the repository root.
- Open http://127.0.0.1:8776/#how-training-works.
- Source: this folder. Build: `python -X utf8 work/consulting-interactive-lesson/build_interactive.py`.
- The original on port 8774 and the centred version on port 8775 are independent.
- Checkout, books, course programmes and PDF generators are copied intact. Payment mode remains PREVIEW.
