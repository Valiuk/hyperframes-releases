import sys,asyncio
from playwright.async_api import async_playwright
async def main(html,times,out):
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg=await b.new_page(viewport={'width':720,'height':450})
        await pg.goto('file://'+html); await pg.wait_for_timeout(300)
        for t in times:
            await pg.evaluate(f'render({t})')
            await pg.screenshot(path=f'{out}_{t}.jpg',type='jpeg',quality=92)
        await b.close()
asyncio.run(main(sys.argv[1],[float(x) for x in sys.argv[2].split(',')],sys.argv[3]))
