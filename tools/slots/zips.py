import json, os, shutil, zipfile
OUT='/home/claude/slots'; REPO='/home/claude/hyperframes-releases'; V='1.0.0'
M=json.load(open(OUT+'/_manifest.json'))
README='''{name} — слот для шаблону Phone Slot Spin (Hyperframes)
============================================================

Що всередині
  install_slot.jsx   — скрипт, що встановлює слот у шаблон
  slot.json          — дані слота (не редагуй)
  symbols/1.png …    — символи; номер файлу = номер символа на сайті й у Конструкторі прокрутів
  symbols.png        — таблиця символів з номерами
  bg.jpg, logo.png   — фон і логотип гри
  FrameGrids/        — рамки під 25 сіток (3–7 барабанів × 3–7 рядів)

Як встановити
  1. Розпакуй архів у будь-яку папку (шлях краще латиницею).
  2. Відкрий у After Effects шаблон Phone Slot Spin.
  3. File › Scripts › Run Script File… → install_slot.jsx.
  4. Вкажи розмір символів (80 % — стандарт) і натисни «Встановити».
  Слот стане наступним номером на слайдері Slot (шар керування в композиції render).

Важливо
  • Не перейменовуй і не переміщуй файли після встановлення — проєкт посилається на них.
    Щоб перенести проєкт на інший ПК: File › Dependencies › Collect Files.
  • Символів у цьому слоті: {count}. Якщо в шаблоні символів більше, вони повторюються по колу.
  • Повторний запуск оновлює слот, а не дублює його. Скасувати — Ctrl+Z.
  • Свої прокрути й виграшні комбінації — «Конструктор прокрутів» на сайті Hyperframes:
    у ньому вибери цей слот, і номери символів збігатимуться з цією таблицею.
'''
out=[]
for m in M:
    tid='slot-'+m['id']; fname='HF-Slot-%s-v%s.zip'%(''.join(w.capitalize() for w in m['id'].split('-')),V)
    dst=os.path.join(REPO,'files',tid); os.makedirs(dst,exist_ok=True); zp=os.path.join(dst,fname)
    top=fname[:-4]; d=OUT+'/'+m['id']
    with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
        z.write('/home/claude/pack_scripts/install_slot.jsx', top+'/install_slot.jsx')
        z.writestr(top+'/ПРОЧИТАЙ.txt', README.format(name=m['name'],count=m['count']))
        for root,_,fs in os.walk(d):
            for f in sorted(fs):
                p=os.path.join(root,f); z.write(p, top+'/'+os.path.relpath(p,d))
    out.append(dict(id=m['id'],tool=tid,file=fname,size=os.path.getsize(zp)))
    print(tid, fname, os.path.getsize(zp)//1024,'KB')
json.dump(out,open(OUT+'/_zips.json','w'),indent=1)
