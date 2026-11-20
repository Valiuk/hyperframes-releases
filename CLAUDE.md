# Hyperframes releases — як додавати реліз

Сайт-каталог: артефакт Claude «Hyperframes — інструменти»
- slug: 9fec3e73-77f4-4cb9-8318-5c82111ea42a
- url: https://claude.ai/artifact/LkP7XP5o5kyAjJY2CzoPMj

Джерело правди — `site/catalog.json`. Сторінка `site/index.html` статична: дані вбудовуються в неї скриптом `site/build.py`.

Новий реліз:
1. Отримати файл від Івана (вкладення в чаті або з його ПК через device-інструменти).
2. `gh release create <tool-id>-v<версія> <файл> -R Valiuk/hyperframes-releases --title "<Назва> <версія>" --notes "<що нового>"`
3. Пряме посилання на файл: `https://github.com/Valiuk/hyperframes-releases/releases/download/<tag>/<ім'я файлу>`
4. У `site/catalog.json` додати в `releases` інструмента `{v, date (YYYY-MM-DD), notes, link}`; поставити статус `release`; оновити `site.updated`. Новий інструмент — новий об'єкт у `tools` (`kind`: ae | app | web | tpl).
5. `cd site && python3 build.py`, опублікувати `site/index.html` в артефакт (publish_files, slug вище, mode patch).
6. Закомітити й запушити зміни в цей репозиторій.
