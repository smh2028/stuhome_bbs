# -*- coding: utf-8 -*-
'''
@author  : smh2208
@software: PyCharm
@file    : parse_util.py
@time    : 2018/8/9 16:03
@desc    :
'''

import re
from scrapy.selector import Selector


def parse_user(text,uid):
    # print('in parse user:',uid)
    sel = Selector(text=text)
    profile = sel.xpath('//div[@class="bm_c u_profile"]')
    if profile.extract():
        item = dict()
        item['name'] = profile.xpath('./div[1]/h2/text()').extract_first().strip()
        uid_full = profile.xpath('./div[1]/h2/span/text()').extract_first()
        item['uid'] = re.search('(\d+)', uid_full).group(1)
        item['signature'] = profile.xpath('./div[1]/ul/li/table//td/text()').extract_first()
        statistical_info = profile.xpath('./div[1]/ul[@class="cl bbda pbm mbm"]/li/a/text()').extract()# re('(\d+)')
        # if statistical_info:
        item['friends_count'] = statistical_info[0]
        item['reply_count'] = statistical_info[3]
        item['theme_count'] = statistical_info[4]
        item['share_count'] = statistical_info[5]
        # pl_info = profile.xpath('./div[1]/ul[4]/li/text()').extract()# 用户没填性别和生日时，这两个可能是毕业院校和学历，故注释掉
        # # if pl_info:
        # gender = pl_info[0]
        # birthday = pl_info[1]
        # # location = pl_info[2]
        activity_node = profile.xpath('./div[@class="pbm mbm bbda cl"]')[-1]
        # print(activity_node)
        item['group'] = activity_node.xpath('./ul[1]//a/text()').extract_first()
        activity_info = activity_node.xpath('./ul[2]//li/text()').extract()[:2]
        # print('activity:',activity_info)
        item['online_time'] = activity_info[0]
        item['register_date'] = activity_info[1]
        score_info = profile.xpath('./div[@id="psts"]/ul/li/text()').extract()
        item['score'] = score_info[1]
        item['water_count'] = score_info[3]
        fields = ['name', 'uid', 'signature', 'friends_count', 'reply_count', 'theme_count', 'share_count','group',
                  'online_time', 'register_date', 'score', 'water_count']
        return item