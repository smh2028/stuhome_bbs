# -*- coding: cp936 -*-


from ctypes import *

def ydm_func(ydm_appid, ydm_appkey, ydm_username, ydm_password, filename, captcha_type):
    """
    ��װ���ƴ��뺯��
    """
    YDMApi = windll.LoadLibrary('yundamaAPI-x64')
    # ��ѯ�������� http://www.yundama.com/price.html
    # ����30���ֽڴ��ʶ����
    result = c_char_p(b"                              ")
    timeout = 10
    captchaId = YDMApi.YDM_EasyDecodeByPath(ydm_username, ydm_password, ydm_appid, ydm_appkey, filename, captcha_type,
                                            timeout, result)
    print("һ��ʶ����֤��ID��%d��ʶ������%s" % (captchaId, result.value))
    return result.value

