# -*- coding: utf-8 -*-
'''
@author  : smh2208
@software: PyCharm
@file    : settings.py
@time    : 2018/8/2 9:27
@desc    :
'''

# 最大线程数
CONCURRENT_THREADS = 20

# 登录用户名
LOGIN_USERNAME = ''
# 登录密码
LOGIN_PASSWORD = ''

# 起始用户uid
START_UID = ''

# Mongodb配置
MONGODB_URI = 'localhost'
MONGODB_DB = 'stuhome'
MONGODB_PORT = 27017
MONGODB_COLLECTION = 'users'

# 刷新页面的延迟，单位s
REFRESH_DELAY = 60

# 当前登录用户的用户名
CURRENT_USERNAME = ''

# 代理ip
PROXIES = {
    'http': '',
    'https': ''
}

# 回复内容
REPLYS = ['水水', '看看', '试试', '666', '水汽来', '福德紧', '不服', '再来', '紫砂', '看看呢', '还有人战吗', '水特么的'
          , '拿点水不容易', '我爱河畔']
