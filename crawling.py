# -*- coding: utf-8 -*-
import copy
import json
import os
import re
import time
from queue import Queue
from threading import Thread
from urllib import parse

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from browser_simulator import browser_simulator
from signature import signature


class Crawling:
    USER_AGENT = ('Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) '
                  'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1')
    HEADERS = {
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1',
        'user-agent': USER_AGENT
    }
    CONCURRENT_WORKER = 4
    DOWNLOAD_DELAY = 2

    class DownloadWorker(Thread):
        MAX_RETRY = 3
        TIMEOUT = 5
        DOWNLOAD_DELAY = 2

        def __init__(self, queue):
            requests.packages.urllib3.disable_warnings()
            Thread.__init__(self)
            self.queue = queue

        def requests_retry_session(self, retries=MAX_RETRY, backoff_factor=0.3, status_forcelist=(500, 502, 504),
                                   session=None):
            session = session or requests.Session()
            retry = Retry(
                total=retries,
                read=retries,
                connect=retries,
                backoff_factor=backoff_factor,
                status_forcelist=status_forcelist,
            )
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            return session

        def run(self):
            while True:
                uri, download_url, target_folder = self.queue.get()
                if self.download(uri, download_url, target_folder):
                    self.queue.task_done()
                time.sleep(self.DOWNLOAD_DELAY)

        def download(self, uri, media_url, target_folder):
            result = False
            headers = copy.copy(Crawling.HEADERS)
            file_name = uri + '.mp4'

            file_path = os.path.join(target_folder, file_name)
            if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
                print('文件{}已存在，跳过下载'.format(file_path))
                return True

            try:
                res = self.requests_retry_session().get(media_url, headers=headers, stream=True, timeout=self.TIMEOUT,
                                                        allow_redirects=False, verify=False)
                resp_url = res.headers['Location']
                resp = requests.get(resp_url, stream=True, timeout=self.TIMEOUT, verify=False)
                with open(file_path, 'wb') as fh:
                    for chunk in resp.iter_content(chunk_size=1024, decode_unicode=True):
                        fh.write(chunk)
                    print('视频已保存到：' + file_path)
                    result = True
            except:
                os.remove(file_path)

            return result

    def __init__(self):
        requests.packages.urllib3.disable_warnings()
        print('正在初始化伪装浏览器')
        browser_simulator.init()
        while True:
            if browser_simulator.READY == 1:
                break
        print('伪装浏览器初始化完成')
        self.ws_endpoint = browser_simulator.ws_endpoint

        current_folder = os.getcwd()
        download_folder = os.path.join(current_folder, 'downloads')
        if not os.path.isdir(download_folder):
            os.mkdir(download_folder)

        self.queue = Queue()
        self.download_failed_urls = []
        # with open('./resource/ws_endpoint', 'r') as f:
        #     self.ws_endpoint = f.readlines()[0]

    def _report_download_failed(self, url):
        self.download_failed_urls.append(url)

    def execute(self, *urls):
        for x in range(self.CONCURRENT_WORKER):
            worker = self.DownloadWorker(self.queue)
            worker.daemon = True
            worker.start()

        for short_url in urls:
            self.generate_task_for_downloading(short_url)
        self.queue.join()

    def get_real_address(self, url: str):
        if url is not None and url.find('v.douyin.com') < 0:
            return url
        while True:
            response = requests.get(url, headers=self.HEADERS, allow_redirects=False, verify=False)
            if response.status_code in (301, 302):
                url = response.headers['Location']
            elif response.status_code == 200:
                return url, response
            else:
                return None, None

    def get_user_id(self, response: requests.Response):
        if not response:
            return None
        user_id = re.findall('uid: "(.*)"', response.text)
        if len(user_id) > 0:
            return user_id[0]
        return None

    def get_dytk(self, response: requests.Response):
        if not response:
            return None
        dytk = re.findall("dytk: '(.*)'", response.text)
        if len(dytk) > 0:
            return dytk[0]
        return None

    def get_tac(self, response: requests.Response):
        if not response:
            return None
        tac = re.search(r"tac='([\s\S]*?)'</script>", response.text)
        if tac is not None:
            return tac.group(1).split('|')[0]

    def generate_task_for_downloading(self, origin_url: str):
        url, response = self.get_real_address(origin_url)

        user_id = self.get_user_id(response)
        dytk = self.get_dytk(response)
        tac = self.get_tac(response)

        params = parse.parse_qs(parse.urlparse(url).query)
        sec_uid = params['sec_uid'][0]

        sign = signature.derive_signature(self.ws_endpoint, tac, user_id, self.USER_AGENT)

        has_more = True
        max_cursor = 0
        response_data = None
        while has_more:
            url = 'https://www.iesdouyin.com/web/api/v2/aweme/post'
            params = {
                'sec_uid': sec_uid,
                'count': '21',
                'max_cursor': max_cursor,
                'aid': '1128',
                '_signature': sign,
                'dytk': dytk
            }
            headers = {
                'USER-AGENT': self.USER_AGENT
            }
            response = requests.get(url, params=params, headers=headers, verify=False)
            if response.ok:
                temp_response_data = json.loads(response.text)

                has_more = temp_response_data['has_more']
                count = len(temp_response_data['aweme_list'])
                if count == 0:
                    has_more = False
                if has_more:
                    max_cursor = temp_response_data['max_cursor']

                if response_data is None:
                    response_data = temp_response_data
                else:
                    response_data['aweme_list'].extend(temp_response_data['aweme_list'])

        if response_data is not None:
            print('共找到{}个视频'.format(len(response_data['aweme_list'])))
            for item in response_data['aweme_list']:  # type: dict
                try:
                    uri = item['video']['download_addr']['uri']
                    url_list = item['video']['download_addr']['url_list']
                    if len(url_list) > 0:
                        download_url = url_list[0].replace('watermark=1', 'watermark=0')
                        current_folder = os.getcwd()
                        target_folder = os.path.join(current_folder, 'downloads/{}'.format(user_id))
                        if not os.path.isdir(target_folder):
                            os.mkdir(target_folder)
                        self.queue.put((uri, download_url, target_folder))
                except:
                    self._report_download_failed(origin_url)


crawling = Crawling()
