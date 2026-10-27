# Separate centred-page layout

The complete training site with a 1600 px maximum page width, equal side margins and a light grey outer background. Mobile gutters shrink to preserve reading space.

- Start from the repository root: `Start-Contained.cmd` or `powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/Start-Contained.ps1 -NoBrowser`.
- Preview: http://127.0.0.1:8775/
- Source: this folder, independent of `work/consulting-card-selection-version`.
- Build: `python -X utf8 work/consulting-contained-version/build_contained.py`.
- Layout additions: `contained-layout.css`. Content, original Bootstrap styling, course selection, electronic books and order documents use this variant's own copied source.
- The original version on port 8774 remains separate and can be continued independently.
- Keep payment mode PREVIEW and private bank/customer data outside Git, as required by the repository AGENTS.md.
