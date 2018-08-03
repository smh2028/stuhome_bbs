```

```

# 清水河畔脚本，刷在线时长，自动水贴回帖
## 安装依赖：

requests==2.18.4

Scrapy==1.5.0

## 使用

`python stuhome_spider.py`

输入username

输入psswpord

如果登录成功会直接进入刷新页面，开始刷新河畔的主页，保持登录状态。登录失败则会返回至重新登录。刷新同时回复大红贴，为了遵守版规，每次回复前会判断最后一个回复的人是否是当前登录用户，避免二连。在settings.py中配置`CURRENT_USER`用户昵称。


## 刷新频率

60s刷新一次，修改settings.py的REFRESH_DELAY可以更改刷新频率

## 代理

如果短时间内失败次数过多，日志输出提示添加代理，则修改settings.py的PROXIES，添加你的代理，重新运行程序。

```python
PROXIES = {
    'http': '111.1.1.1',
    'https': '111.1.1.1'
}
```
