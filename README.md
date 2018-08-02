# 清水河畔脚本，刷在线时长，自动水贴回帖
## 安装依赖：

requests==2.18.4

Scrapy==1.5.0

## 使用

`python stuhome_spider.py`

输入username

输入psswpord

如果登录成功会直接进入刷新页面，开始刷新河畔的主页，保持登录状态。登录失败则会返回至重新登录

## 刷新频率

10s刷新一次，修改settings.py的REFRESH_DELAY可以更改刷新频率