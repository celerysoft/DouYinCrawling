# -*- coding: utf-8 -*-
"""
使用signature请求数据时，USER-AGENT必须与获取signature时的USER-AGENT保持一致，signature具有有效期，在有效期内可无限使用
"""
import asyncio
from pyppeteer import connect


class Signature:
    DEFAULT_USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/78.0.3904.108 Safari/537.36')

    def derive_signature(self, ws_endpoint, tac, user_id, user_agent):
        return self.gen(ws_endpoint, tac, user_id, user_agent)

    async def _sign(self, ws_endpoint, tac, user_id, user_agent=None):
        browser = await connect(browserWSEndpoint=ws_endpoint)
        pages = await browser.pages()
        page = pages[0]
        if user_agent is None or len(user_agent) == 0:
            user_agent = self.DEFAULT_USER_AGENT
        await page.setUserAgent(user_agent)
        sign = await page.evaluate('generateSignature', tac, user_id)
        return sign

    def gen(self, ws_endpoint, tac, user_id, user_agent=None):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        sign = loop.run_until_complete(self._sign(ws_endpoint, tac, user_id, user_agent))
        return sign


signature = Signature()
