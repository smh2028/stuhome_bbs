# -*- coding: utf-8 -*-
'''
@author  : smh2208
@software: PyCharm
@file    : settings.py
@time    : 2018/8/2 9:27
@desc    :
'''

LOG_SUCC = 1  # 登录成功状态
LOG_FAILED = 2  # 登录失败状态，用户名或者密码错误
LOG_NEEDPROXIES = 3  # 登录失败过多，需要等待15min或者设置代理，实测只要10min不到

# 最大线程数
CONCURRENT_THREADS = 20

# 登录用户名
LOGIN_USERNAME = ''
# 登录密码
LOGIN_PASSWORD = ''

# 起始用户uid
START_UID = ''

# 云打码appid
YDM_APPID = ''
# 云打码appkey
YDM_APPKEY = ''
# 云打码用户名
YDM_USERNAME = ''
# 云打码密码
YDM_PASSWORD = ''


# 刷新页面的延迟，单位s
REFRESH_DELAY = 60

# 代理ip
PROXIES = {
    'http': '',
    'https': ''
}
