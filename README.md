# Hyperframes — релізи

Плагіни для After Effects, програми та веб-інструменти Hyperframes.
Усі файли — у розділі [Releases](https://github.com/Valiuk/hyperframes-releases/releases).

## catalog.json — каталог для інших сайтів

Постійне посилання (завжди остання версія):
https://raw.githubusercontent.com/Valiuk/hyperframes-releases/main/catalog.json

Формат (`schema: 1`):
- `updated` — дата останнього оновлення каталогу;
- `tools[]` — лише інструменти, які можна скачати:
  - `id`, `name`, `description`;
  - `type`: `ae-plugin` | `app` | `web-tool` | `ae-template`, `type_label` — підпис українською;
  - `hosts` — програми, де працює плагін (`After Effects`, `Premiere Pro`);
  - `version`, `date` (YYYY-MM-DD), `notes` — що нового в останній версії;
  - `installer` — `true`, якщо в архіві є `install.bat`;
  - `warning` — важливе попередження або `null`;
  - `downloads[]` — `{label, url, size}`; `url` завжди починається з `https://github.com/`, `size` у байтах.

Поля можуть додаватися, але наявні не перейменовуються й не видаляються без зміни `schema`.
