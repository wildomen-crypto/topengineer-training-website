TOPENGINEER — ЦВЕТА КУРСОВ: КАРТОЧКИ И КАЛЬКУЛЯТОР

Это готовая текущая цветная версия самостоятельного проекта.
Для запуска из корня репозитория: Start-Windows.cmd.
Или из этой папки: powershell.exe -NoProfile -ExecutionPolicy Bypass -File Start-preview.ps1
Оставить окно сервера открытым; PHP нужен для формы и PDF.

Главная: http://127.0.0.1:8771/
Калькулятор: http://127.0.0.1:8771/#training-calculator
Программы: http://127.0.0.1:8771/#course-programmes
Форма реквизитов: http://127.0.0.1:8771/training-order/
При занятом порте из корня: powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/Start-Windows.ps1 -Port 8774

Начальный расчёт: Level 1, 2 дня, 1 участник, EUR 450.
Четыре курса, 352 темы. Part 1 и Part 2 одновременно видны на широком экране.
Режим документов PREVIEW. Реальные банковские инструкции не включены.

Для Codex: открыть корень репозитория и прочитать AGENTS.md, CODEX_HANDOFF.md,
PROJECT_CONTEXT.md и README.md. Старые версии и прежний компьютер не нужны.
Исходники: work/consulting-course-colours/. Не редактировать только готовый outputs.
Пересборка из корня: python -X utf8 work/consulting-course-colours/build_parallel.py
