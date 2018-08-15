# -*- coding: cp936 -*-


from ctypes import *

def ydm_func(appid, appkey, ydm_username, ydm_password, file, captcha_type):
    """
    封装的云打码函数
    :param appid:
    :param appkey:
    :return:
    """
    YDMApi = windll.LoadLibrary('yundamaAPI-x64')
    appId = appid
    appKey = appkey
    username = ydm_username
    password = ydm_password
    print('\r\n>>>正在一键识别...')
    # 例：1004表示4位字母数字，不同类型收费不同。请准确填写，否则影响识别率。在此查询所有类型 http://www.yundama.com/price.html
    codetype = captcha_type
    # 分配30个字节存放识别结果
    result = c_char_p(b"                              ")
    timeout = 10
    # 验证码文件路径
    filename = file
    # 一键识别函数，无需调用 YDM_SetAppInfo 和 YDM_Login，适合脚本调用
    captchaId = YDMApi.YDM_EasyDecodeByPath(username, password, appId, appKey, filename, codetype, timeout, result)
    print("一键识别：验证码ID：%d，识别结果：%s" % (captchaId, result.value))
    return result.value

