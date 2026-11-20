# Hyperframes releases — як додавати реліз

Сайт-каталог: артефакт Claude «Hyperframes — інструменти»
- slug: 9fec3e73-77f4-4cb9-8318-5c82111ea42a
- url: https://claude.ai/artifact/LkP7XP5o5kyAjJY2CzoPMj

Джерело правди — `site/catalog.json`. Сторінка `site/index.html` статична: дані вбудовуються в неї скриптом `site/build.py`.

Новий реліз:
1. Отримати файл від Івана (вкладення в чаті або з його ПК через device-інструменти).
2. Плагін AE (CEP): встановлені плагіни лежать у `C:/Program Files (x86)/Common Files/Adobe/CEP/extensions` і `C:/Users/vania/AppData/Roaming/Adobe/CEP/extensions`. Перед публікацією перевірити файли на ключі API та особисті шляхи. Пакувати в zip з install.bat (див. `tools/pack.py`: папка плагіна + install.bat, що копіює в %APPDATA% і вмикає PlayerDebugMode, + ВСТАНОВЛЕННЯ.txt).
   GitHub Releases з сесії Claude недоступні (403), тому файл кладемо в репо: `files/<tool-id>/<Назва>-v<версія>.zip` (до 100 МБ на файл).
   Файли понад 100 МБ (програми) Іван сам завантажує в GitHub Releases (тег `<tool-id>-v<версія>`); посилання беремо через `gh api repos/Valiuk/hyperframes-releases/releases`. Кілька файлів в одному релізі — поле `files: [{label, file, size, link}]`.
3. Пряме посилання: `https://github.com/Valiuk/hyperframes-releases/raw/main/files/<tool-id>/<файл>`
4. У `site/catalog.json` додати в `releases` інструмента `{v, date (YYYY-MM-DD), notes, link}`; поставити статус `release`; оновити `site.updated`. Новий інструмент — новий об'єкт у `tools` (`kind`: ae | app | web | tpl). Для плагінів — `hosts`: ["ae"] або ["ae","pr"] за `Host Name` у CSXS/manifest.xml (PPRO = Premiere); вкладка «Працюють у Premiere» фільтрує за `pr`.
5. `cd site && python3 build.py`, опублікувати `site/index.html` в артефакт (publish_files, slug вище, mode patch).
6. Закомітити й запушити зміни в цей репозиторій.

## Правки Івана на сайті
Власник редагує каталог прямо на сторінці (кнопка «Редагувати»): зміни лежать у базі артефакту, документ `overrides/main` = `{deleted:{id:true}, edits:{id:{name,kind,status,desc,hidden,hideFiles:[file]}}}`. Відвідувачі, що увійшли в Claude, бачать їх одразу; вбудований у HTML каталог — ні.
Перед кожним оновленням сайту: прочитати `overrides/main` (db_get), перенести правки в `site/catalog.json` (видалені — прибрати з `tools`), закомітити, потім очистити документ (db_write set `{deleted:{},edits:{}}`) і опублікувати сторінку.
