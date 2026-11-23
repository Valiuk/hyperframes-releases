import json,re
d=json.load(open('catalog.json',encoding='utf8'))
s=json.dumps(d,ensure_ascii=False).replace('</','<\\/')
h=open('index.html',encoding='utf8').read()
blk='<script type="application/json" id="data">'+s+'</script>'
if 'id="data"' in h: h=re.sub(r'<script type="application/json" id="data">.*?</script>',lambda m:blk,h,flags=re.S)
else: h=h.replace('\n<script>\n{','\n'+blk+'\n<script>\n{',1)
open('index.html','w',encoding='utf8').write(h)
print(len(d['tools']))

# ---- Публічний catalog.json у корені репо (для Obriy/SynkVela та інших) ----
TYPE={'ae':('ae-plugin','Плагін AE'),'app':('app','Програма'),'web':('web-tool','Веб-інструмент'),'tpl':('ae-template','Шаблон AE')}
HOST={'ae':'After Effects','pr':'Premiere Pro'}
def rel_sorted(t): return sorted([r for r in t.get('releases',[]) if r.get('v')],key=lambda r:r.get('date',''),reverse=True)
def dl_of(r):
    fs=r['files'] if len(r.get('files',[]))>1 else [{'label':'Завантажити','link':r.get('link'),'size':r.get('size')}]
    return [{'label':f.get('label') or 'Завантажити','url':f['link'],'size':f.get('size')} for f in fs if str(f.get('link','')).startswith('https://github.com/')]
out=[]
for t in d['tools']:
    if t.get('hidden'): continue
    rs=rel_sorted(t)
    if not rs: continue
    r=rs[0]
    files=r['files'] if len(r.get('files',[]))>1 else [{'label':'Завантажити','link':r.get('link'),'size':r.get('size'),'file':r.get('file')}]
    dls=[{'label':f.get('label') or 'Завантажити','url':f['link'],'size':f.get('size')} for f in files if str(f.get('link','')).startswith('https://github.com/')]
    if not dls: continue
    names=' '.join(str(f.get('file') or f['link']) for f in files)
    installer=t['kind']=='ae' and t['id']!='extract-layers' or t['id']=='yt-fragment'
    out.append({'id':t['id'],'name':t['name'],'type':TYPE[t['kind']][0],'type_label':TYPE[t['kind']][1],
      'description':t.get('desc',''),'hosts':[HOST[h] for h in t.get('hosts',[])],
      'version':r['v'],'date':r.get('date'),'notes':r.get('notes',''),
      'installer':installer,'warning':t.get('warn'),'downloads':dls,
      **({'video':{'url':d['site']['video_base'].rstrip('/')+'/site/'+t['video'],'label':'Як працює'}} if t.get('video') and d['site'].get('video_base') else {}),
      'releases':[{'version':x['v'],'date':x.get('date'),'notes':x.get('notes',''),'downloads':dl_of(x)} for x in rs if dl_of(x)]})
pub={'schema':1,'name':'Hyperframes — інструменти','updated':d['site'].get('updated'),
     'page':'https://claude.ai/artifact/LkP7XP5o5kyAjJY2CzoPMj','tools':out}
json.dump(pub,open('../catalog.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
print('public catalog:',len(out))
