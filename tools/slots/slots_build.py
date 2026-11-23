import os, json, shutil, glob
from PIL import Image
SRC='/home/claude/src'; PK='/home/claude/pack/Slots_pack'; OUT='/home/claude/slots'
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
FO=json.load(open(SRC+'/frames_old.json')); FN=json.load(open(PK+'/_meta_frames.json')); AN=json.load(open(PK+'/_meta_assets.json'))
def trimmed(src, dst):
    im=Image.open(src).convert('RGBA'); a=im.getchannel('A')
    im=im.crop(a.point(lambda v:255 if v>8 else 0).getbbox()); a=im.getchannel('A')
    b=a.point(lambda v:255 if v>160 else 0).getbbox() or (0,0,im.width,im.height)
    im.save(dst); return [b[0],b[1],b[2]-b[0],b[3]-b[1]]
SL=[
 dict(id='coin-strike', code='CS', layer='Coin Strike', name='Coin Strike', maker='Playson',
      syms=[SRC+'/CoinStrike_15symbols/symbols/symbol (%d).png'%i for i in range(1,16)], bg=SRC+'/cs/bg.jpg', logo=SRC+'/cs/logo.png',
      frames=[SRC+'/FrameGrids/FCS', SRC+'/Grids_7x7/FrameGrids/FCS'], fmeta=FO['CS']),
 dict(id='pink-joker', code='JK', layer='Joker', name='Pink Joker', maker='Playson',
      syms=[SRC+'/Joker_symbols/symbols/%d.png'%i for i in range(1,17)], bg=SRC+'/Joker_skin/bg.jpg', logo=SRC+'/Joker_skin/logo.png',
      frames=[SRC+'/Joker_skin/FrameGrids/FJK', SRC+'/Grids_7x7/FrameGrids/FJK'], fmeta=FO['JK']),
 dict(id='coin-volcano', code='CV', layer='Coin Volcano', name='Coin Volcano', maker='3 Oaks',
      syms=[SRC+'/TMD-6110_to_Vulcan/assets/symbols/%d.png'%i for i in range(1,9)], bg=SRC+'/TMD-6110_to_Vulcan/assets/volcano_bg.jpg', logo=SRC+'/TMD-6110_to_Vulcan/assets/volcano_logo.png',
      frames=[SRC+'/CoinVolcano_skin/FrameGrids/FCV', SRC+'/Grids_7x7/FrameGrids/FCV'], fmeta=FO['CV']),
]
NEW={'BH':('burning-hot-40','40 Burning Hot','EGT'),'BR':('book-of-ra','Book of Ra','Novomatic'),'FG':('fortune-garuda-500','Fortune Garuda 500',''),
     'FT':('fortune-tiger','Fortune Tiger','PG Soft'),'MF':('mystic-fortune','Mystic Fortune','Play\'n GO'),'SC':('shining-crown','Shining Crown','EGT'),
     'DB':('double-bubble','Double Bubble','Gamesys'),'SE':('sun-of-egypt','Sun of Egypt','Booongo')}
for code,(sid,name,maker) in NEW.items():
    a=AN[code]; d=PK+'/'+a['dir']
    SL.append(dict(id=sid, code=code, layer=a['name'], name=name, maker=maker, syms=[d+'/symbols/%d.png'%i for i in range(1,a['count']+1)],
                   bg=d+'/bg.jpg', logo=d+'/logo.png', frames=[d+'/FrameGrids'], fmeta=FN[code], mult={'BR':1.25,'SC':1.25,'MF':1.2}.get(code,1)))
manifest=[]
for s in SL:
    d=OUT+'/'+s['id']; os.makedirs(d+'/symbols'); os.makedirs(d+'/FrameGrids')
    boxes=[trimmed(f, d+'/symbols/%d.png'%i) for i,f in enumerate(s['syms'],1)]
    Image.open(s['bg']).convert('RGB').save(d+'/bg.jpg',quality=92)
    lb=trimmed(s['logo'], d+'/logo.png')
    for fd in s['frames']:
        for f in glob.glob(fd+'/g*.png'): shutil.copy(f, d+'/FrameGrids/'+os.path.basename(f))
    have=sorted(os.path.basename(f)[1:-4] for f in glob.glob(d+'/FrameGrids/g*.png'))
    assert len(have)==25 and all(k in s['fmeta'] for k in have), (s['id'], len(have))
    m=dict(id=s['id'], code=s['code'], layer=s['layer'], name=s['name'], maker=s['maker'], count=len(boxes), box=boxes, logobox=lb,
           mult=s.get('mult',1), frames={k:s['fmeta'][k] for k in have}, version='1.0.0')
    json.dump(m, open(d+'/slot.json','w'), ensure_ascii=False)
    manifest.append({k:m[k] for k in ('id','code','layer','name','maker','count')})
    print(s['id'], len(boxes), 'symbols')
json.dump(manifest, open(OUT+'/_manifest.json','w'), ensure_ascii=False, indent=1)
