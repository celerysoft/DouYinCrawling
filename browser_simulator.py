# -*- coding: utf-8 -*-
import asyncio

# import pyppdf.patch_pyppeteer 能自动下载 chromium
import pyppdf.patch_pyppeteer
from pyppeteer.launcher import launch


class BrowserSimulator:
    def __init__(self):
        self.READY = 0
        self.ws_endpoint = ''

    @property
    def _disable_webdriver_js_code(self):
        return """
        () => Object.defineProperties(navigator,{
            webdriver: {
                get: () => false
            }
        })
        """

    async def _connect_chrome(self):
        browser = await launch(headless=True, args=['--no-sandbox'])
        # with open('./resource/ws_endpoint', 'w') as f:
        #     f.write(browser.wsEndpoint)
        self.ws_endpoint = browser.wsEndpoint
        page = await browser.pages()
        page = page[0]
        await page.setUserAgent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36')
        await page.evaluate(self._disable_webdriver_js_code)
        await page.goto('file:///Users/Celery/Developer/Python/DouYinCrawling/templates/index.html')
        self.READY = 1
        # await page.goto("http://127.0.0.1:5001/")
        # await asyncio.sleep(10)
        # await asyncio.sleep(20000000)
        # await page.close()
        # await browser.close()

    def init(self):
        asyncio.get_event_loop().run_until_complete(self._connect_chrome())


browser_simulator = BrowserSimulator()
# browser_simulator.init()
