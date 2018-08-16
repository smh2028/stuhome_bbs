# 清水河畔用户信息爬虫


## 安装依赖：

requests==2.18.4

Scrapy==1.5.0



## 爬取配置

#### 配置用户名和密码

```python
LOGIN_USERNAME = '张三'
LOGIN_PASSWORD = 'abc'
```

#### 配置起始uid，建议设置成当前登录用户的uid

```python
START_UID = '123'
```

#### 配置MongoDB

```
MONGODB_URI = 'localhost'
MONGODB_DB = 'stuhome'
MONGODB_PORT = 27017
MONGODB_COLLECTION = 'users_info'
```

#### 开始爬取

`python stuhome_spider.py`

首先模拟登录，登录成功后从START_UID开始爬取该uid的用户信息并存入MongoDB，并爬取该用户的所有好友的uid，再根据这些uid爬取好友的好友，直至爬取论坛所有注册用户。




## 验证码的处理

#### 使用代理或者打码方式绕过验证码

如果短时间内登录失败次数过多，日志输出“登录失败次数过多，请等待15min或输入验证码！”，可以选择修改settings.py的PROXIES，添加你的代理，重新运行程序。

```python
PROXIES = {
    'http': '111.1.1.1',
    'https': '111.1.1.1'
}
```
也可以接入代码平台，注册云打码，配置以下信息：

```python
# 云打码appid
YDM_APPID = ''
# 云打码appkey
YDM_APPKEY = ''
# 云打码用户名
YDM_USERNAME = ''
# 云打码密码
YDM_PASSWORD = ''
```

也可以选择等待几分钟之后再试。


## 更新日志：

* ##### v0.1.2  &nbsp;&nbsp; 2018.08.08

     * 添加登录失败次数过多后的验证码破解，把验证码图片写入文件手动输入破解。
		##### v0.1.3	&nbsp;&nbsp; 2018.08.09

     * 多线程

* ##### v0.1.4 &nbsp;&nbsp;  2018.08.10

     * 用户信息去重
     
* ##### v0.1.5 &nbsp;&nbsp;  2018.08.15

     * 接入打码平台，修复好友页数解析bug
     




## To do:

* requests.exceptions.ConnectionError: ('Connection aborted.', ConnectionResetError(10054, '远程主机强迫关闭了一个现有的连接。', None, 10054, None))
* 爬虫可能会遇到很多用户的好友都相同，导致队列中无元素可以获取，所有进程都被迫停止。解决办法:
     * 开始时往队列里多添加几个好友数多的活跃用户 
     * 更改获取好友策略，从水区帖子内容获得用户uid,去重复杂，上scrapy