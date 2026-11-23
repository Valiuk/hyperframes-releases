import json, os, shutil, zipfile
OUT='/home/claude/slots'; REPO='/home/claude/hyperframes-releases'; V='1.1.0'
M=json.load(open(OUT+'/_manifest.json'))
README='''{name} — слот-гра для After Effects (Hyperframes)
=======================================================

Що всередині
  build_slot.jsx     — ГОЛОВНИЙ скрипт: збирає екран гри з нуля в новому проєкті
  install_slot.jsx   — лише для повного шаблону Phone Slot Spin (додає гру в його перемикач)
  slot.json          — дані слота (не редагуй)
  symbols/1.png …    — символи; номер файлу = номер символа на сайті й у Конструкторі прокрутів
  symbols.png        — таблиця символів з номерами
  bg.jpg, logo.png   — фон і логотип гри
  FrameGrids/        — рамки під 25 сіток (3–7 барабанів × 3–7 рядів)

Як зібрати гру (великий шаблон не потрібен)
  1. Розпакуй архів у постійну папку (шлях краще латиницею) — проєкт посилатиметься на ці файли.
  2. After Effects → File › Scripts › Run Script File… → build_slot.jsx.
  3. Вибери розмір символів і сітку, натисни «Зібрати».
  Вийде композиція render 1080×1920: фон, лого, рамка й барабани з трьома прокрутами.
    • Сітка — слайдери Reels і Rows на шарі Controls (рамка перемикається сама).
    • Прокрути — ключі шару «Null 2» у композиції Slot (крок — 266 px = один символ).
    • Свої комбінації — Конструктор прокрутів на сайті + apply_spin_plan.jsx.

Важливо
  • Символів у цьому слоті: {count}. Не перейменовуй файли — проєкт посилається на них.
  • Перенести проєкт на інший ПК: File › Dependencies › Collect Files.
  • Скасувати збірку — Ctrl+Z.
'''
out=[]
for m in M:
    tid='slot-'+m['id']; fname='HF-Slot-%s-v%s.zip'%(''.join(w.capitalize() for w in m['id'].split('-')),V)
    dst=os.path.join(REPO,'files',tid); os.makedirs(dst,exist_ok=True); zp=os.path.join(dst,fname)
    top=fname[:-4]; d=OUT+'/'+m['id']
    with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
        z.write('/home/claude/hyperframes-releases/tools/slots/build_slot.jsx', top+'/build_slot.jsx')
        z.write('/home/claude/hyperframes-releases/tools/slots/install_slot.jsx', top+'/install_slot.jsx')
        z.writestr(top+'/ПРОЧИТАЙ.txt', README.format(name=m['name'],count=m['count']))
        for root,_,fs in os.walk(d):
            for f in sorted(fs):
                p=os.path.join(root,f); z.write(p, top+'/'+os.path.relpath(p,d))
    out.append(dict(id=m['id'],tool=tid,file=fname,size=os.path.getsize(zp)))
    print(tid, fname, os.path.getsize(zp)//1024,'KB')
json.dump(out,open(OUT+'/_zips.json','w'),indent=1)
