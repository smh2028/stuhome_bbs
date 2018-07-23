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
import threading

#官方大红帖：http://bbs.uestc.edu.cn/forum.php?mod=viewthread&tid=1655504

class StuhomeSpider():
    username = ''
    password = ''
    log_page_url = 'http://bbs.uestc.edu.cn/member.php?mod=logging&action=login'
    log_in_url = 'http://bbs.uestc.edu.cn/member.php?mod=logging&action=login&loginsubmit=yes&loginhash={}&inajax=1'
    home_url = 'http://bbs.uestc.edu.cn/'
    tiezi_url = 'http://bbs.uestc.edu.cn/forum.php?mod=viewthread&tid=1727470&extra=page%3D1'
    reply_url = 'http://bbs.uestc.edu.cn/forum.php?mod=post&action=reply&fid={0}&tid={1}&extra={2}&replysubmit=yes' \
                '&infloat=yes&handlekey=fastpost&inajax=1'
    reply_message = 'test data from pp'
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
        #代理测试
        # proxies = {
        #     'http':'82.202.70.132:8080',
        #     'https':'82.202.70.132:8080'
        # }
        response = self.session.post(self.log_in_url.format(self.loginhash),headers=self.headers,data=post_data
                                     )#,proxies=proxies
        #打印登录结果
        # print(response.text)
        if 'succeedmessage' in response.text:
            return True
        return False

    def get_tiezi_params_and_reply(self):
        '''根据帖子的url获取参数并发表回复'''
        response = self.session.get(self.tiezi_url,headers=self.headers)
        # print(response.text)
        sel = Selector(text=response.text)
        fid = sel.xpath('//a[@href="curforum"]/@fid').extract_first()
        tid = re.search('tid=(\d+)',self.tiezi_url).group(1)
        if 'extra' in self.tiezi_url:
            extra = re.search('extra=(.*)', self.tiezi_url).group(1)
        else:
            extra = ''
        formhash = sel.xpath('//input[@name="formhash"]/@value').extract_first()
        self.reply(fid,tid,extra,formhash)

    def reply(self,fid,tid,extra,formhash):
        '''回复某一个帖子'''
        post_data = {
            'message': self.reply_message,
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
            self.session.get(self.home_url, headers=self.headers)
            print(datetime.datetime.now(),':刷新主页成功，离升级又近了一步，嘿嘿')
            # 水大红贴，慎重打开，容易被封
            # self.get_tiezi_params_and_reply()
            # print('大红贴水贴成功，嘿嘿')
            sleep(10)


    def run(self):
        self.username = input('请输入用户名：')
        self.password = input('请输入密码：')
        login_result = self.log_in()
        if login_result:
            willing2reply = input('登录成功！是否要水贴？ y/n:')
            if willing2reply=='y':
                self.tiezi_url = input('请输入要回复的帖子url：')
                self.reply_message = input('请输入要回复的内容：')
                self.get_tiezi_params_and_reply()
            else:
                print('开始刷新主页')
        refresh_thread = threading.Thread(target=self.refresh)
        refresh_thread.start()


if __name__ == '__main__':
    stuhome_sp = StuhomeSpider()
    stuhome_sp.run()

