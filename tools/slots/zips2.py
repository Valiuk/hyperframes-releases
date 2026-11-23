import os, zipfile
REPO='/home/claude/hyperframes-releases/files'; O='/mnt/user-data/outputs'
def mk(tid, fname, items, readme):
    d=os.path.join(REPO,tid); os.makedirs(d,exist_ok=True); zp=os.path.join(d,fname); top=fname[:-4]
    with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr(top+'/ПРОЧИТАЙ.txt', readme)
        for src,arc in items: z.write(src, top+'/'+arc)
    print(tid, fname, os.path.getsize(zp)//1024, 'KB')
mk('slot-spin-plan','HF-Spin-Plan-v1.0.0.zip',
   [(O+'/spinplan/index.html','spin_constructor.html'),(O+'/spinplan/apply_spin_plan.jsx','apply_spin_plan.jsx'),(O+'/spinplan/original_plan.json','example_original_plan.json')],
'''Прокрутки для шаблону Phone Slot Spin (Hyperframes)
===================================================

spin_constructor.html — Конструктор прокрутів. Відкривається в браузері (подвійний клік).
apply_spin_plan.jsx   — скрипт для After Effects, що будує прокрути за планом.
example_original_plan.json — приклад: прокрути як в оригінальному шаблоні.

Як зробити свої прокрути
  1. Встанови потрібний слот у шаблон (архів HF-Slot-…, скрипт install_slot.jsx)
     і перемкни на нього слайдер Slot у композиції render.
  2. Відкрий spin_constructor.html. Угорі вибери той самий слот — палітра покаже його символи
     з тими самими номерами, що на сайті.
  3. Вибери сітку (барабани × ряди), додай прокрути, задай час і намалюй, що випадає в кожній клітинці.
     «Старт» — що видно до першого прокруту. Кнопка «Грати» показує прев'ю.
  4. «Скопіювати план».
  5. У After Effects: File › Scripts › Run Script File… → apply_spin_plan.jsx, встав план, «Застосувати».

Що робить скрипт
  • рух — звичайні ключі на шарі «Null plan» у композиції Slot (можна правити руками);
  • комбінації — стрічки ColumnPlan_N: кадр 0 — старт, кадр 1 — після першого прокруту і т. д.;
    перемикання посеред прокруту — HOLD-ключі Time Remap на шарах ColumnPlan_N;
  • оригінальні барабани вимикаються (око). Повернути — увімкни Column_N і вимкни ColumnPlan_N.
  Повторний запуск з новим планом перебудовує все. Скасувати — Ctrl+Z.
''')
mk('phone-slot-spin','HF-Phone-Slot-Spin-Scripts-v1.0.0.zip',
   [(O+'/export_variation.jsx','export_variation.jsx'),(O+'/add_spacing_controls.jsx','add_spacing_controls.jsx'),(O+'/add_slot_rig.jsx','add_slot_rig.jsx'),
    (O+'/resize_skin_symbols.jsx','resize_skin_symbols.jsx'),(O+'/fix_spin_mechanism.jsx','fix_spin_mechanism.jsx')],
'''Скрипти для шаблону Phone Slot Spin (Hyperframes)
=================================================
Запуск кожного: File › Scripts › Run Script File… Усе скасовується одним Ctrl+Z.

export_variation.jsx     — зберігає окремий легкий проєкт лише з вибраними слотами і сіткою.
                           Оригінал не змінюється. Слоти перенумеровуються 1…N (номери — у коментарі шару керування).
add_spacing_controls.jsx — слайдери Gap X / Gap Y: відступи між барабанами й рядами, рамка розширюється разом.
add_slot_rig.jsx         — нуль «Slot rig» у композиції Game: масштабуй і рухай барабани разом із рамкою.
resize_skin_symbols.jsx  — розмір символів одного слота відносно лінійки (напр. 80 %).
fix_spin_mechanism.jsx   — вирівнює зупинки барабанів (без дрейфу) і додає параметричні прокрути на слайдерах.

Порядок: спершу add_spacing_controls, потім add_slot_rig (його можна запускати повторно).
''')
