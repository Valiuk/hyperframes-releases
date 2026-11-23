"""Витягує вбудовані ігри шаблону Phone Slot Spin з PSD (pragmatic_symbol_1..9, pragmatic_BG, pragmatic_Logo).
Шар PSD з індексом i (згори) відповідає слоту: 1..15 -> i=20-slot, 16->3, 17->2, 18->1, 19->0 (i=4 — Book of Ra, пропускаємо)."""
import sys, os, json
from psd_tools import PSDImage
from PIL import Image
PSD = sys.argv[1]; OUT = sys.argv[2]
GAMES = ['Big Bass Bonanza','Buffalo King','Cowboy Coins',"Da Vinci's Treasure",'Fire Stampede','Gates of Olympus','Gold Rush',
         'Great Rhino','Madame Destiny','Sugar Rush','Sweet Bonanza','The Dog House Megaways','Wolf Gold','Lucky Dragons',
         '3 Genie Wishes','Gates of Olympus 1000','Sweet Bonanza 1000','Fruit Party','Gravity Bonanza']
def pidx(slot): return 20 - slot if slot <= 15 else {16: 3, 17: 2, 18: 1, 19: 0}[slot]
def trim(im):
    a = im.getchannel('A'); bb = a.point(lambda v: 255 if v > 8 else 0).getbbox()
    return im.crop(bb) if bb else im
sym = [list(PSDImage.open(f'{PSD}/pragmatic_symbol_{n}.psd')) for n in range(1, 10)]
bgp = list(PSDImage.open(f'{PSD}/pragmatic_BG.psd')); lgp = list(PSDImage.open(f'{PSD}/pragmatic_Logo.psd'))
meta = []
for slot, name in enumerate(GAMES, 1):
    i = pidx(slot); d = os.path.join(OUT, '%02d' % slot); os.makedirs(d + '/symbols', exist_ok=True)
    for n in range(9):
        L = sym[n][i]
        im = L.composite(viewport=(0, 0, 512, 512)).convert('RGBA')   # як видно в компі 512×512
        trim(im).save(f'{d}/symbols/{n+1}.png')
    bg = bgp[i].composite().convert('RGB'); bg.save(d + '/bg.jpg', quality=90)
    lg = trim(lgp[i].composite().convert('RGBA')); lg.save(d + '/logo.png')
    meta.append(dict(slot=slot, name=name, psd=[sym[0][i].name, bgp[i].name, lgp[i].name], bg=bg.size, logo=lg.size))
    print(slot, name, '| sym1:', sym[0][i].name[:28], '| bg:', bgp[i].name[:24], bg.size, '| logo:', lgp[i].name[:24], lg.size, flush=True)
json.dump(meta, open(OUT + '/_builtin.json', 'w'), ensure_ascii=False, indent=1)
