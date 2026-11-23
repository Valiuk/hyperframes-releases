import sys,asyncio,subprocess
from playwright.async_api import async_playwright
async def main(html,dur,out):
    ff=subprocess.Popen(['ffmpeg','-loglevel','error','-y','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-c:v','libx264','-crf','26','-preset','veryfast','-pix_fmt','yuv420p','-movflags','+faststart',out+'.tmp.mp4'],stdin=subprocess.PIPE)
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg=await b.new_page(viewport={'width':720,'height':450})
        await pg.goto('file://'+html); await pg.wait_for_timeout(300)
        for i in range(int(dur*30)):
            await pg.evaluate(f'render({i/30})')
            ff.stdin.write(await pg.screenshot(type='jpeg',quality=92))
        await b.close()
    ff.stdin.close(); assert ff.wait()==0
    import os; os.replace(out+'.tmp.mp4',out)
asyncio.run(main(sys.argv[1],float(sys.argv[2]),sys.argv[3]))
