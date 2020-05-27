# -*- coding: utf-8 -*-
import sys

from crawling import crawling


if __name__ == '__main__':
    # https://v.douyin.com/J1tgwoB/

    # https://www.iesdouyin.com/share/user/52046820042?sec_uid=MS4wLjABAAAAs00stL_91LKEmm4gbWsEFgCUnl_8ySHe5kVhrVwT9hg&u_code=j9e8ik1a&utm_campaign=client_share&app=aweme&utm_medium=ios&tt_from=copy&utm_source=copy

    if len(sys.argv) >= 2:
        url = sys.argv[1]
    else:
        url = input('请输入抖音用户个人主页的链接，按下回车确认：')

    print('正在解析，解析完毕将自动进行下载')
    crawling.execute(url)







