import json,re
d=json.load(open('catalog.json',encoding='utf8'))
s=json.dumps(d,ensure_ascii=False).replace('</','<\\/')
h=open('index.html',encoding='utf8').read()
blk='<script type="application/json" id="data">'+s+'</script>'
if 'id="data"' in h: h=re.sub(r'<script type="application/json" id="data">.*?</script>',lambda m:blk,h,flags=re.S)
else: h=h.replace('\n<script>\n{','\n'+blk+'\n<script>\n{',1)
open('index.html','w',encoding='utf8').write(h)
print(len(d['tools']))
