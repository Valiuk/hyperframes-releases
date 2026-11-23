import json, os, base64, io
from PIL import Image, ImageDraw, ImageFont
OUT='/home/claude/slots'; SITE='/home/claude/site_slots'; os.makedirs(SITE, exist_ok=True)
M=json.load(open(OUT+'/_manifest.json'))
def font(sz):
    for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf']:
        if os.path.exists(p): return ImageFont.truetype(p, sz)
    return ImageFont.load_default()
F=font(22)
thumbs={}
for m in M:
    d=OUT+'/'+m['id']; n=m['count']; cols=min(n,8); rows=(n+cols-1)//cols; C=150; P=10
    S=Image.new('RGBA',(cols*(C+P)+P, rows*(C+P)+P),(24,25,30,255)); dr=ImageDraw.Draw(S)
    tb=[]
    for i in range(n):
        im=Image.open(d+'/symbols/%d.png'%(i+1)).convert('RGBA'); im.thumbnail((C-24,C-24),Image.LANCZOS)
        x=P+(i%cols)*(C+P); y=P+(i//cols)*(C+P)
        dr.rounded_rectangle((x,y,x+C,y+C),12,fill=(40,42,50,255))
        S.alpha_composite(im,(x+(C-im.width)//2, y+(C-im.height)//2+6))
        dr.rounded_rectangle((x+6,y+6,x+44,y+36),8,fill=(45,140,235,255))
        t=str(i+1); w=dr.textlength(t,font=F); dr.text((x+25-w/2,y+8),t,font=F,fill=(255,255,255,255))
        # мініатюра для конструктора
        th=Image.open(d+'/symbols/%d.png'%(i+1)).convert('RGBA'); th.thumbnail((72,72),Image.LANCZOS)
        b=io.BytesIO(); th.save(b,'WEBP',quality=80,method=6); tb.append('data:image/webp;base64,'+base64.b64encode(b.getvalue()).decode())
    S.save(d+'/symbols.png'); S.save(SITE+'/'+m['id']+'.webp','WEBP',quality=84,method=6)
    thumbs[m['id']]=tb
    print(m['id'], S.size, os.path.getsize(SITE+'/'+m['id']+'.webp')//1024,'KB')
json.dump(thumbs, open('/home/claude/slots/_thumbs.json','w'))
print('thumbs total', os.path.getsize('/home/claude/slots/_thumbs.json')//1024,'KB')
