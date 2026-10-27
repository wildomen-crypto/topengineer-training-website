# Отдельная версия с улучшениями удобства

Это самостоятельный вариант сайта для сравнения с исходной цветной версией. Изменения и программы этого варианта находятся в `work/consulting-usability-version/`, готовая страница — в `outputs/consulting-usability-version/`. Исходная версия находится в `work/consulting-course-colours/` и `outputs/consulting-course-colours/`.

Запуск на Windows из корня проекта:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/Start-Usability.ps1 -NoBrowser
```

Откройте http://127.0.0.1:8773/. Сервер нужно оставить запущенным. При занятом порте передайте, например, `-Port 8774`. Заказы и документы работают в демонстрационном режиме; приватные реквизиты в этот вариант не включены.

Для пересборки из корня проекта:

```powershell
python -X utf8 work/consulting-usability-version/build_usability.py
```

После любых изменений проверяйте мобильный калькулятор, добавление и удаление курса, возврат из формы к расчёту, дату, две части программы и загрузку КП. Платёжный режим не включать до подтверждения банковских и налоговых условий.

Проверка серверной части при запущенном локальном сервере (нужны Python, `requests` и `PyMuPDF`): `python tests/test_usability_variant.py`.
