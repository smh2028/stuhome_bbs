# -*- coding: utf-8 -*-
'''
@author  : smh2208
@software: PyCharm
@file    : stuhome_spider.py
@time    : 2018/7/22 9:31
@desc    :
'''

import requests,re
from scrapy.selector import Selector
from time import time,sleep
import datetime
import threading,logging
from random import choice
from settings import REFRESH_DELAY, PROXIES, REPLYS, CURRENT_USERNAME
from urllib.parse import urlencode,urljoin

#官方大红帖：http://bbs.uestc.edu.cn/forum.php?mod=viewthread&tid=1655504

LOG_SUCC = 1
LOG_FAILED = 2
LOG_NEEDPROXIES = 3

class StuhomeSpider():
    username = ''
    password = ''
    log_page_url = 'http://bbs.uestc.edu.cn/member.php?mod=logging&action=login'
    log_in_url = 'http://bbs.uestc.edu.cn/member.php?mod=logging&action=login&loginsubmit=yes&loginhash={}&inajax=1'
    home_url = 'http://bbs.uestc.edu.cn/'
    tiezi_url = 'http://bbs.uestc.edu.cn/forum.php?mod=viewthread&tid=1655504'
    dahong_url = 'http://bbs.uestc.edu.cn/forum.php?mod=viewthread&tid=1655504'
    reply_url = 'http://bbs.uestc.edu.cn/forum.php?mod=post&action=reply&fid={0}&tid={1}&extra={2}&replysubmit=yes' \
                '&infloat=yes&handlekey=fastpost&inajax=1'
    # reply_message = 'test data from pp'
    session = requests.session()
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                     'Chrome/67.0.3396.99 Safari/537.36',
    }

    def __init__(self):
        '''获得fromhash和loginhash'''
        response = self.session.get(self.log_page_url)
        sel = Selector(text=response.text)
        input_id = sel.xpath('//input[@name="username"]/@id').extract_first()
        input_formhash = sel.xpath('//input[@name="formhash"]/@value').extract_first()
        #获得登录post请求的loginhash和formhash
        self.loginhash = re.search('username_(.*)',input_id).group(1)
        self.formhash = input_formhash
        self.logger = logging.getLogger('Stuhome')
        # print(self.formhash)


    def log_in(self):
        '''登录'''
        post_data = {
            "formhash": self.formhash,
            "referer": "http://bbs.uestc.edu.cn/",
            "loginfield": "username",
            "username": self.username,#quote(string=username,encoding='utf-8')
            "password": self.password,
            "questionid": "0",
            "answer": "",
        }
        self.session.headers.update(self.headers)
        response = self.session.post(self.log_in_url.format(self.loginhash),headers=self.headers,data=post_data
                                     ,proxies=PROXIES)
        #打印登录结果
        # print(response.text)
        if 'succeedmessage' in response.text:
            return LOG_SUCC
        elif '请输入验证码后继续登录' in response.text:
            # self.crack_captcha(response.text)
            return LOG_NEEDPROXIES
        return LOG_FAILED

    def crack_captcha(self,text):
        '''破解验证码'''
        pass

    def check(self):
        """判断大红贴最后一个回复的人是不是我自己"""
        params = {
            'mod': 'viewthread',
            'tid': '1655504',
            'extra': '',
            'page': self.page_num
        }
        base_url = 'http://bbs.uestc.edu.cn/forum.php?'
        url = urljoin(base_url, urlencode(params))
        response = self.session.get(url, headers=self.headers)
        sel = Selector(text=response.text)
        last = sel.xpath('//div[@id="postlist"]//div[@class="authi"]/a/text()').extract()[-2]
        print('lastname',last)
        if last == CURRENT_USERNAME:
            return True
        return False


    def get_tiezi_params_and_reply(self):
        '''根据帖子的url获取参数并发表回复'''
        response = self.session.get(self.tiezi_url,headers=self.headers)
        # print(response.text)

        sel = Selector(text=response.text)
        self.page_num = re.search('(\d*) 页',response.text,re.M).group(1)
        print('总页数',self.page_num)

        fid = sel.xpath('//a[@href="curforum"]/@fid').extract_first()
        tid = re.search('tid=(\d+)',self.tiezi_url).group(1)
        if 'extra' in self.tiezi_url:
            extra = re.search('extra=(.*)', self.tiezi_url).group(1)
        else:
            extra = ''
        formhash = sel.xpath('//input[@name="formhash"]/@value').extract_first()

        self.logger.warning('checking')
        # 如果最后一个回复的人不是我才回复
        if not self.check():
            self.reply(fid,tid,extra,formhash)

    def reply(self,fid,tid,extra,formhash):
        '''回复某一个帖子'''
        post_data = {
            'message': choice(REPLYS),
            'posttime': str(int(time())),
            'formhash': formhash,
            'usesig': '1',
            'subjec': '++',
        }
        r = self.session.post(url=self.reply_url.format(fid, tid, extra), data=post_data, headers=self.headers)
        if 'succeedhandle_fastpost' in r.text:
            print('回复成功！')
        else:
            print('回复失败！')

    def refresh(self):
        '''定时刷新主页，保持登录状态，刷在线时长，美滋滋'''
        while True:
            # 刷新河畔主页
            self.session.get(self.home_url, headers=self.headers)
            print(datetime.datetime.now(),':刷新主页成功，离升级又近了一步，嘿嘿')
            # 水大红贴
            self.get_tiezi_params_and_reply()
            sleep(REFRESH_DELAY)


    def run(self):
        self.username = input("请输入用户名：")
        self.password = input("请输入密码：")
        login_result = self.log_in()
        if login_result == LOG_SUCC:

            self.logger.warning('登录成功，现在开始刷新')
            refresh_thread = threading.Thread(target=self.refresh)
            refresh_thread.start()
        elif login_result == LOG_NEEDPROXIES:
            self.logger.warning('失败次数太多，请设置代理')
        else:
            self.logger.warning('用户名或密码错误，登录失败，请重试！')
            self.run()

if __name__ == '__main__':
    stuhome_sp = StuhomeSpider()
    stuhome_sp.run()

