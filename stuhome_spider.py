# -*- coding: utf-8 -*-
'''
@author  : smh2208
@software: PyCharm
@file    : stuhome_spider.py
@time    : 2018/7/22 9:31
@desc    :
'''

import requests,re,time,logging,datetime
from scrapy.selector import Selector
from time import time,sleep
from random import choice
from settings import *
from urllib.parse import unquote
from ydm_api import ydm_func
import tkinter as tk
from tkinter import ttk, messagebox

winW = 370
winH = 100

LOG_SUCC = 1  # 登录成功状态
LOG_FAILED = 2  # 登录失败状态，用户名或者密码错误
LOG_NEEDPROXIES = 3  # 登录失败过多，需要等待15min或者设置代理，实测只要10min不到

class StuhomeSpider():
    """河畔用户信息爬虫"""
    username = ''
    password = ''
    log_page_url = 'http://bbs.uestc.edu.cn/member.php?mod=logging&action=login'
    log_in_url = 'http://bbs.uestc.edu.cn/member.php?mod=logging&action=login&loginsubmit=yes&loginhash={}&inajax=1'
    home_url = 'http://bbs.uestc.edu.cn/'

    def __init__(self,):
        """获得fromhash和loginhash以及其他初始化"""
        self.session = requests.session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
        self.session.mount('http://', adapter)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/67.0.3396.99 Safari/537.36',
        }
        self.session.headers.update(headers)
        # self.ua = UserAgent()
        # 获得登录post请求的loginhash和formhash
        response = self.session.get(self.log_page_url, proxies=PROXIES)
        sel = Selector(text=response.text)
        input_id = sel.xpath('//input[@name="username"]/@id').extract_first()
        input_formhash = sel.xpath('//input[@name="formhash"]/@value').extract_first()
        self.loginhash = re.search('username_(.*)',input_id).group(1)
        self.formhash = input_formhash

    def log_in(self, username, password):
        """登录"""
        post_data = {
            "formhash": self.formhash,
            "referer": "http://bbs.uestc.edu.cn/",
            "loginfield": "username",
            "username": username,
            "password": password,
            "questionid": "0",
            "answer": "",
        }
        response = self.session.post(self.log_in_url.format(self.loginhash), data=post_data, proxies=PROXIES)
        if 'succeedmessage' in response.text:
            return LOG_SUCC
        elif '请输入验证码后继续登录' in response.text:
            result = self.crack_captcha(response.text)
            if result:
                return LOG_SUCC
        return LOG_FAILED

    def crack_captcha(self,text):
        """破解验证码"""
        auth_url = re.search("location.href='(.*)'</script>", text).group(1)
        try:
            # 第1步，获得loginhash_qr,formhash_qr和updateseccode
            response = self.session.get('http://bbs.uestc.edu.cn/'+auth_url, proxies=PROXIES)
            self.loginhash_qr = re.search('loginhash=(.*?)"',response.text).group(1)
            sel = Selector(text=response.text)
            self.formhash_qr = sel.xpath('//input[@name="formhash"]/@value').extract_first()
            # print(response.text)
            updateseccode = re.search("updateseccode\('(.*?)',",response.text).group(1)

            # 抓包时有这个请求，无返回内容，猜测是通知服务器准备接受验证码校验请求，注释掉无影响
            # sendmail_url = 'http://bbs.uestc.edu.cn/home.php?mod=misc&ac=sendmail&rand='+str(int(time()))
            # self.session.get(sendmail_url)

            # 第2步，构造验证码的url，0.6877971157202973似乎是无影响的随机数，固定使用了某次抓包时获得的值，无影响
            url = 'http://bbs.uestc.edu.cn/misc.php?mod=seccode&action=update&idhash={}&0.6877971157202973&modid=' \
                  'member::logging'.format(updateseccode)
            r = self.session.get(url, proxies=PROXIES)
            captcha_url = 'http://bbs.uestc.edu.cn/'+re.findall('src="(.*?)"', r.text)[-1]
            # 获得验证码图片的请求headers需要添加Refer参数
            header2 = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/67.0.3396.99 Safari/537.36',
                'Referer': 'http://bbs.uestc.edu.cn/'+auth_url,
            }
            response2 = self.session.get(captcha_url,headers=header2, proxies=PROXIES)

            # 3. 验证码写入文件
            with open('captcha.png','wb') as f:
                f.write(response2.content)

            # 4. 手工输入验证码或者接入打码平台
            qr = input('请输入验证码,验证码captcha.png文件在软件根目录下！')
            # qr = ydm_func(YDM_APPID, YDM_APPKEY, YDM_USERNAME, YDM_PASSWORD, b'captcha.png',1004)
            auth = re.search('auth=(.*?)&',auth_url).group(1)
            seccodehash = captcha_url.split('=')[-1]
            post_data = {
                "formhash": self.formhash_qr,
                "referer": "http://bbs.uestc.edu.cn/",
                "auth": unquote(auth),
                "seccodehash": seccodehash,
                "seccodemodid": "member::loggin",
                "seccodeverify": qr
            }
            print('再登录参数',post_data)

            # 5. 服务器验证验证码
            check_url = 'http://bbs.uestc.edu.cn/misc.php?mod=seccode&action=check&inajax=1&modid=member::' \
                        'logging&idhash={}&secverify={}'.format(seccodehash, qr)
            check_resp = self.session.get(check_url, proxies=PROXIES)
            print(check_resp.status_code,check_resp.text) # 服务器验证成功

            # 6. 加上验证码信息post登录
            header3 = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/67.0.3396.99 Safari/537.36',
                'Referer': 'http://bbs.uestc.edu.cn/'+auth_url
            }
            response = self.session.post(self.log_in_url.format(self.loginhash_qr), headers=header3,data=post_data,
                                         proxies=PROXIES)

            #7.打印登录结果,判断是否登录成功
            # print('打印输入验证码之后的登录结果')
            if 'succeedmessage' in response.text:
                return True
            return False
        except Exception as e:
            print(e.args)
            return False


    def refresh(self):
        """定时刷新主页，保持登录状态，刷在线时长"""
        while True:
            # 刷新河畔主页
            try:
                self.session.get(self.home_url)
            except:
                break
            print(datetime.datetime.now(), ':刷新主页成功，离升级又近了一步')
            sleep(REFRESH_DELAY)

    def update_useragent(self):
        """随机更换User-Agent"""
        headers = {
            'User-Agent': self.ua.random
        }
        self.session.headers.update(headers)

    # test func
    def run(self):
        """启动函数"""
        login_result = self.log_in(LOGIN_USERNAME, LOGIN_PASSWORD)
        if login_result == LOG_SUCC:
            print('登录成功')
        elif login_result == LOG_NEEDPROXIES:
            print('登录失败次数过多，请等待15min或输入验证码！')
        else:
            print('用户名或密码错误，登录失败，请重试！')

# 使用方法
# if __name__ == '__main__':
#     stuhome_sp = StuhomeSpider()
#     stuhome_sp.run()



