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
4. У `site/catalog.json` додати в `releases` інструмента `{v, date (YYYY-MM-DD), notes, link}`; поставити статус `release`; оновити `site.updated`. Новий інструмент — новий об'єкт у `tools` (`kind`: ae | app | web | tpl). Червоне попередження на картці — поле `warn`. Анімоване відео-пояснення (показ при наведенні) — поле `video: "videos/<id>.mp4"`; файл лежить у `site/videos/` і публікується разом з index.html (publish_files, as `videos/<id>.mp4`). Шаблон і рендер — `tools/videos/` (HTML-сцена з render(t), rec.py → mp4 720×450, 30 fps). Для плагінів — `hosts`: ["ae"] або ["ae","pr"] за `Host Name` у CSXS/manifest.xml (PPRO = Premiere); вкладка «Працюють у Premiere» фільтрує за `pr`.
5. `cd site && python3 build.py` (заодно генерує публічний `catalog.json` у корені — його читає Obriy/SynkVela, формат описано в README; не ламати наявні поля), опублікувати `site/index.html` в артефакт (publish_files, slug вище, mode patch).
6. Закомітити й запушити зміни в цей репозиторій.

## Правки Івана на сайті
Власник редагує каталог прямо на сторінці (кнопка «Редагувати»): зміни лежать у базі артефакту, документ `overrides/main` = `{deleted:{id:true}, edits:{id:{name,kind,status,desc,hidden,hideFiles:[file]}}}`. Відвідувачі, що увійшли в Claude, бачать їх одразу; вбудований у HTML каталог — ні.
Перед кожним оновленням сайту: прочитати `overrides/main` (db_get), перенести правки в `site/catalog.json` (видалені — прибрати з `tools`), закомітити, потім очистити документ (db_write set `{deleted:{},edits:{}}`) і опублікувати сторінку.

## Obriy / SynkVela (читає кореневий catalog.json раз на годину)
- Сервер читає лише catalog.json; архіви качає браузер, редіректи GitHub дозволяти не треба.
- Додаткові файли каталогу: поле `"include": ["https://raw.githubusercontent.com/Valiuk/hyperframes-releases/main/<файл>.json"]`, до 10, лише з цього репо.
- Історія версій: `releases[{version,date,notes,downloads}]` — уже генерується build.py.
- Відео-пояснення: коли будуть для плагінів — додати в публічний каталог поле `video` з абсолютним https-URL (напр. raw.githubusercontent.com/.../site/videos/<id>.mp4) і сказати Івану повідомити Obriy.

## Шаблони AE: слоти для Phone Slot Spin (kind `tpl`)
- Картки: `phone-slot-spin` (скрипти шаблону), `slot-spin-plan` (Конструктор прокрутів + apply_spin_plan.jsx), `slot-<гра>` — по одній на слот.
- Слот = архів `files/slot-<id>/HF-Slot-<Name>-v<версія>.zip`: `build_slot.jsx` (головний — збирає екран гри з нуля в новому проєкті, `tools/slots/build_slot.jsx`; структура сумісна з apply_spin_plan: render.layer(1)=Controls з Reels/Rows, Slot з «Null 2» і Column_N, Symbol_N→pragmatic_symbol_N) + `install_slot.jsx` (лише для повного шаблону) + `slot.json` (layer — ім'я шару скіна в шаблоні, code — для FG_<code>, count, box, logobox, mult, frames) + `symbols/N.png` + `bg.jpg` + `logo.png` + `FrameGrids/g{C}x{R}.png` (25 сіток 3..7×3..7) + `symbols.png`.
- НОМЕР СИМВОЛА СВЯТИЙ: N.png = Symbol_N = номер у таблиці на сайті (`site/slots/<id>.webp`, поле `symbols`) = номер у Конструкторі (мініатюри вбудовані в spin_constructor.html). Не перенумеровувати в наступних версіях — додавати лише в кінець.
- Новий слот: символи/фон/лого від Івана → `tools/slots/` (frames.py малює тематичну рамку, якщо своєї немає) → zip → таблиця символів → запис у catalog.json → оновити Конструктор (SLOTS) і архів slot-spin-plan.
- Поля картки: `guide` — кроки «Як користуватися»; `symbols: {img, count}` — таблиця символів (файл публікується разом з index.html як `slots/<id>.webp`). Картки з `symbols` не показуються на таймлайні.
- Повний шаблон .aep (1,2 ГБ) — у GitHub Releases, тег `phone-slot-spin-v1.0.0`, файл `phone.slot.spin.v1.converted.folder.zip`; на картці `phone-slot-spin` першою кнопкою. Іван хоче, щоб для слотів великий шаблон був не потрібен — основний шлях build_slot.jsx.
- Вбудовані ігри шаблону (19 шт., Pragmatic Play): code `P01..P19`, витягнуті з PSD шаблону (`tools/slots/extract_builtin.py` → `builtin_build.py`; індекс шару PSD: слоти 1..15 → 20-слот, 16→3, 17→2, 18→1, 19→0). По 9 символів. Book of Ra / Mystic Fortune — окремі слоти, вже додані раніше.
