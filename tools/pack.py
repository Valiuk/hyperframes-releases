import os,zipfile,json
C='/mnt/user-data/uploads/Common Files--Adobe--CEP--extensions/'
R='/mnt/user-data/uploads/Roaming--Adobe--CEP--extensions/'
M=[('scribe-subs',C+'ae-transcribe','AE-Transcribe','1.0.0','AE Transcribe'),
('sync-lip',C+'com.hyperframes.aesync','Sync-Lip','1.0.0','Sync Lip'),
('iyo-spaces',C+'com.hyperframes.iyospaces','iyo-Spaces','1.4.0','iyo Spaces'),
('asset-library',C+'com.hyperframes.library','Hyperframes-Library','1.0.0','Hyperframes Library'),
('smart-rename',C+'com.hyperframes.smartrename','Smart-Rename','1.1.1','Smart Rename'),
('ae-kit',C+'com.ivan.aekit','AE-Kit','1.0.0','AE Kit'),
('currency-fiddler',C+'CurrencyFiddler','Currency-Fiddler','1.0.0','Currency Fiddler'),
('phone-insert',C+'HF_ScreenFit','HF-Screen-Fit','0.3.2','HF Screen Fit'),
('split-screen',C+'HF_SplitScreen','HF-Split-Screen','1.0.0','HF Split Screen'),
('hf-elastic',C+'hf-elastic','Hyperframes-Elastic','1.0.0','Hyperframes Elastic'),
('ae-upscale',C+'HFUpscale','Hyperframes-Upscale-AE','1.0.0','Hyperframes Upscale'),
('facecut',R+'FaceCut','FaceCut','1.0.0','Face Cut'),
('propainter',R+'HF_ProPainter','HF-ProPainter','1.0.0','HF ProPainter'),
('remove-bg',R+'HF_RemoveBG','HF-RemoveBG','1.0.0','HF RemoveBG'),
('ai-assistant',R+'com.hyperframes.aeagent','Hyperframes-Agent','1.0.1','Hyperframes Agent'),
('spine-export',R+'com.hyperframes.spineexport','Spine-Export','1.0.0','Hyperframes Spine Export'),
('text-styles',R+'com.hyperframes.textstyles','HF-Text-Styles','0.17.1','HF Text Styles'),
('yt-fragment',R+'YTFragment','YT-Fragment-AE','1.0.0','YT Fragment'),
]
BAT=r'''@echo off
setlocal
set "SRC=%~dp0{folder}"
set "DST=%APPDATA%\Adobe\CEP\extensions\{folder}"
echo Installing {menu} for After Effects...
if not exist "%APPDATA%\Adobe\CEP\extensions" mkdir "%APPDATA%\Adobe\CEP\extensions"
if exist "%DST%" rmdir /s /q "%DST%"
xcopy "%SRC%" "%DST%\" /e /i /y /q >nul
for %%v in (9 10 11 12 13) do reg add "HKCU\Software\Adobe\CSXS.%%v" /v PlayerDebugMode /t REG_SZ /d 1 /f >nul
echo.
echo Done. Restart After Effects and open: Window ^> Extensions ^> {menu}
pause
'''
TXT='''{menu} {ver} — плагін для Adobe After Effects (Hyperframes)

ВСТАНОВЛЕННЯ (Windows)
1. Розпакуй архів.
2. Запусти install.bat — він скопіює плагін у %APPDATA%\\Adobe\\CEP\\extensions
   і увімкне непідписані розширення (PlayerDebugMode).
3. Перезапусти After Effects: Window > Extensions > {menu}

ВРУЧНУ / macOS
Скопіюй папку {folder} у:
  Windows: %APPDATA%\\Adobe\\CEP\\extensions\\
  macOS:   ~/Library/Application Support/Adobe/CEP/extensions/
і увімкни PlayerDebugMode = 1 для CSXS.9–12
  (macOS: defaults write com.adobe.CSXS.11 PlayerDebugMode 1 — і так для 9, 10, 12).
'''
out=[]
for tid,src,name,ver,menu in M:
    folder=os.path.basename(src)
    zp=f'zips/{name}-v{ver}.zip'
    with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
        for root,_,files in os.walk(src):
            for f in files:
                p=os.path.join(root,f); z.write(p,os.path.join(folder,os.path.relpath(p,src)))
        z.writestr('install.bat',BAT.format(folder=folder,menu=menu).replace('\n','\r\n'))
        z.writestr('ВСТАНОВЛЕННЯ.txt',TXT.format(menu=menu,ver=ver,folder=folder).replace('\n','\r\n').encode('utf-8-sig'))
    out.append(dict(id=tid,file=os.path.basename(zp),ver=ver,size=os.path.getsize(zp),menu=menu))
json.dump(out,open('plan.json','w'),ensure_ascii=False,indent=1)
for o in out: print(f"{o['id']:18s} {o['file']:40s} {o['size']/1e6:6.2f}MB")
