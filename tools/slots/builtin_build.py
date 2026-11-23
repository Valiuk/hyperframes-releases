import os, json, shutil, glob, re
from PIL import Image
B='/home/claude/builtin'; FR='/home/claude/bframes'; OUT='/home/claude/slots'
FM=json.load(open(FR+'/frames_builtin.json')); META=json.load(open(B+'/_builtin.json'))
def trimbox(p):
    im=Image.open(p).convert('RGBA'); b=im.getchannel('A').point(lambda v:255 if v>160 else 0).getbbox() or (0,0,im.width,im.height)
    return [b[0],b[1],b[2]-b[0],b[3]-b[1]]
def slug(n): return re.sub(r'[^a-z0-9]+','-',n.lower().replace("'",'')).strip('-')
man=json.load(open(OUT+'/_manifest.json')); man=[m for m in man if not m['code'].startswith('P')]
for m in META:
    k='%02d'%m['slot']; sid=slug(m['name']); d=OUT+'/'+sid
    shutil.rmtree(d,ignore_errors=True); os.makedirs(d+'/symbols'); os.makedirs(d+'/FrameGrids')
    boxes=[]
    for n in range(1,10):
        shutil.copy(f'{B}/{k}/symbols/{n}.png', f'{d}/symbols/{n}.png'); boxes.append(trimbox(f'{d}/symbols/{n}.png'))
    Image.open(f'{B}/{k}/bg.jpg').save(d+'/bg.jpg',quality=88)
    shutil.copy(f'{B}/{k}/logo.png', d+'/logo.png')
    for f in glob.glob(f'{FR}/FrameGrids/F{k}/*.png')+glob.glob(f'{FR}/Grids_7x7/FrameGrids/F{k}/*.png'): shutil.copy(f, d+'/FrameGrids/')
    s=dict(id=sid, code='P'+k, layer=m['name'], name=m['name'], maker='Pragmatic Play', count=9, box=boxes, logobox=trimbox(d+'/logo.png'),
           mult=1, frames=FM[k], version='1.1.0', builtin=m['slot'])
    assert len(glob.glob(d+'/FrameGrids/*.png'))==25
    json.dump(s,open(d+'/slot.json','w'),ensure_ascii=False)
    man.append({x:s[x] for x in ('id','code','layer','name','maker','count')}); print(sid)
json.dump(man,open(OUT+'/_manifest.json','w'),ensure_ascii=False,indent=1)
