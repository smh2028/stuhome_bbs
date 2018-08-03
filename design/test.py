# -*- coding: utf-8 -*-
'''
@author  : smh2208
@software: PyCharm
@file    : test.py
@time    : 2018/8/3 18:17
@desc    :
'''

from urllib.parse import urlencode,urljoin

base_url = 'http://bbs.uestc.edu.cn/forum.php?'
parmas = {
            'mod': 'viewthread',
            'tid': '1655504',
            'extra': '',
            'page': 3
        }

r = urlencode(parmas)
print(r)
url = urljoin(base_url,r)
print(url)