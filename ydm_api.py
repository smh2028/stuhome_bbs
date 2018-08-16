# -*- coding: cp936 -*-


from ctypes import *

def ydm_func(ydm_appid, ydm_appkey, ydm_username, ydm_password, filename, captcha_type):
    """
    封装的云打码函数
    """
    YDMApi = windll.LoadLibrary('yundamaAPI-x64')
    # 查询所有类型 http://www.yundama.com/price.html
    # 分配30个字节存放识别结果
    result = c_char_p(b"                              ")
    timeout = 10
    captchaId = YDMApi.YDM_EasyDecodeByPath(ydm_username, ydm_password, ydm_appid, ydm_appkey, filename, captcha_type,
                                            timeout, result)
    print("一键识别：验证码ID：%d，识别结果：%s" % (captchaId, result.value))
    return result.value

