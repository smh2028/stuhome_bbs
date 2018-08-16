# -*- coding: utf-8 -*-
'''
@author  : smh2208
@software: PyCharm
@file    : stuhome_spider.py
@time    : 2018/7/22 9:31
@desc    :
'''

import requests,re,pymongo,time,logging,json,datetime
from scrapy.selector import Selector
from time import time,sleep
from random import choice
from settings import *
from urllib.parse import urlencode,urljoin, unquote
from parse_util import parse_user
from queue import Queue,Empty
from threading import Thread,Lock
from ydm_api import ydm_func
from fake_useragent import UserAgent

# 爬虫可能会遇到很多用户的好友都相同，导致队列中无元素可以获取，所有进程都被迫停止
# 解决办法: 1.开始时往队列里多添加几个好友数多的活跃用户 TODO
#          2.更改获取好友策略，从水区帖子内容获得用户uid,难度高，上scrapy

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
    # 大红贴地址
    welfare_url = 'http://bbs.uestc.edu.cn/forum.php?mod=viewthread&tid=1655504'
    reply_url = 'http://bbs.uestc.edu.cn/forum.php?mod=post&action=reply&fid={0}&tid={1}&extra={2}&replysubmit=yes' \
                '&infloat=yes&handlekey=fastpost&inajax=1'
    friend_url = 'http://bbs.uestc.edu.cn/home.php?mod=space&uid={}&do=friend&from=space&page={}'

    def __init__(self):
        """获得fromhash和loginhash以及其他初始化"""
        self.session = requests.session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
        self.session.mount('http://', adapter)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/67.0.3396.99 Safari/537.36',
        }
        self.session.headers.update(headers)
        self.ua = UserAgent()
        # 获得登录post请求的loginhash和formhash
        response = self.session.get(self.log_page_url, proxies=PROXIES)
        sel = Selector(text=response.text)
        input_id = sel.xpath('//input[@name="username"]/@id').extract_first()
        input_formhash = sel.xpath('//input[@name="formhash"]/@value').extract_first()
        self.loginhash = re.search('username_(.*)',input_id).group(1)
        self.formhash = input_formhash
        self.logger = logging.getLogger('Stuhome')
        # 获得Mongodb的collection对象
        self.co = pymongo.MongoClient(MONGODB_URI, MONGODB_PORT)[MONGODB_DB][MONGODB_COLLECTION]
        self.queue = Queue()
        self.filter = set()
        self.locker = Lock()
        self.queue.put(START_UID)
        # 避免重复爬取第一个用户
        self.filter.add(START_UID)
        logging.basicConfig(filename='bbs.log', filemode="w", level=logging.DEBUG)

    def log_in(self):
        """登录"""
        post_data = {
            "formhash": self.formhash,
            "referer": "http://bbs.uestc.edu.cn/",
            "loginfield": "username",
            "username": self.username,
            "password": self.password,
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
        print('验证码出现')
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
            # qr = input('请输入验证码：')
            qr = ydm_func(YDM_APPID, YDM_APPKEY, YDM_USERNAME, YDM_PASSWORD, b'captcha.png',1004)
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
        response = self.session.get(url)
        sel = Selector(text=response.text)
        last = sel.xpath('//div[@id="postlist"]//div[@class="authi"]/a/text()').extract()[-2]
        print('last reply:',last)
        if last == CURRENT_USERNAME:
            return True
        return False


    def get_tiezi_params_and_reply(self):
        """根据帖子的url获取参数并发表回复"""
        response = self.session.get(self.welfare_url)
        sel = Selector(text=response.text)
        self.page_num = re.search('(\d*) 页',response.text,re.M).group(1)
        print('总页数',self.page_num)
        fid = sel.xpath('//a[@href="curforum"]/@fid').extract_first()
        tid = re.search('tid=(\d+)', self.welfare_url).group(1)
        if 'extra' in self.welfare_url:
            extra = re.search('extra=(.*)', self.welfare_url).group(1)
        else:
            extra = ''
        formhash = sel.xpath('//input[@name="formhash"]/@value').extract_first()
        self.logger.warning('checking')
        # 如果最后一个回复的人不是我才回复
        if not self.check():
            self.reply(fid,tid,extra,formhash)

    def reply(self,fid,tid,extra,formhash):
        """回复某一个帖子"""
        post_data = {
            'message': choice(REPLYS),
            'posttime': str(int(time())),
            'formhash': formhash,
            'usesig': '1',
            'subjec': '++',
        }
        r = self.session.post(url=self.reply_url.format(fid, tid, extra), data=post_data)
        if 'succeedhandle_fastpost' in r.text:
            print('回复成功！')
        else:
            print('回复失败！')

    def refresh(self):
        """定时刷新主页，保持登录状态，刷在线时长"""
        while True:
            # 刷新河畔主页
            try:
                self.session.get(self.home_url)
            except:
                break
            print(datetime.datetime.now(), ':刷新主页成功，离升级又近了一步，嘿嘿')
            sleep(REFRESH_DELAY)

    def update_useragent(self):
        """随机更换User-Agent"""
        headers = {
            'User-Agent': self.ua.random
        }
        self.session.headers.update(headers)

    def crawl(self,i):
        """爬取用户信息"""
        while True:
            try:
                uid = self.queue.get(timeout=10)
            except Empty as e:
                logging.warning('线程{} 退出 {}'.format(i,time.ctime()))
                break
            # 解析用户信息，写入Mongodb
            profile_url = 'http://bbs.uestc.edu.cn/home.php?mod=space&uid={}&do=profile'.format(uid)
            self.update_useragent()
            profile_resp = self.session.get(profile_url)
            item = parse_user(profile_resp.text, uid)
            if item:
                logging.warning('saving item {}'.format(json.dumps(item)))
                self.co.insert_one(item)

            # 解析好友信息，获得所有好友的uid并加入queue
            frinds_url = self.friend_url.format(uid,1)
            friends_resp = self.session.get(frinds_url)
            sel = Selector(text=friends_resp.text)
            foot_node = sel.xpath('//div[@class="mtm pgs cl"]')
            # 好友数不止一页
            if foot_node:
                pagenum = foot_node.xpath('./div/label/span/text()').extract_first()
                pagenum = int(pagenum.split(' ')[2])
                # print('pagenum',pagenum,type(pagenum))
            # 好友数只有1页
            else:
                pagenum = 1
            if pagenum:
                for page in range(1,pagenum+1):
                    url = self.friend_url.format(uid,page)
                    self.update_useragent()
                    resp = self.session.get(url)
                    sel = Selector(text=resp.text)
                    hrefs = sel.xpath('//ul[@class="buddy cl"]/li/div[1]/a/@href').extract()
                    for href in hrefs:
                        uid2 = href.split('=')[-1]
                        if uid2 not in self.filter:
                            logging.warning('friend uid:{}'.format(uid2))
                            self.queue.put(uid2)
                            with self.locker:
                                self.filter.add(uid2)

    def run(self):
        """启动函数"""
        self.username = LOGIN_USERNAME
        self.password = LOGIN_PASSWORD
        login_result = self.log_in()
        if login_result == LOG_SUCC:
            self.logger.warning('登录成功')
            # 多线程爬取用户信息
            threads = []
            for i in range(CONCURRENT_THREADS):
                thread = Thread(target=self.crawl,args=(i,))
                thread.start()
                threads.append(thread)
            for t in threads:
                t.join()
        elif login_result == LOG_NEEDPROXIES:
            self.logger.warning('登录失败次数过多，请等待15min或输入验证码！')
        else:
            self.logger.warning('用户名或密码错误，登录失败，请重试！')


if __name__ == '__main__':
    stuhome_sp = StuhomeSpider()
    stuhome_sp.run()

