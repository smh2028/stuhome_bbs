# -*- coding: cp936 -*-


from ctypes import *

def ydm_func(appid, appkey, ydm_username, ydm_password, file, captcha_type):
    """
    ��װ���ƴ��뺯��
    :param appid:
    :param appkey:
    :return:
    """
    YDMApi = windll.LoadLibrary('yundamaAPI-x64')
    appId = appid
    appKey = appkey
    username = ydm_username
    password = ydm_password
    print('\r\n>>>����һ��ʶ��...')
    # ����1004��ʾ4λ��ĸ���֣���ͬ�����շѲ�ͬ����׼ȷ��д������Ӱ��ʶ���ʡ��ڴ˲�ѯ�������� http://www.yundama.com/price.html
    codetype = captcha_type
    # ����30���ֽڴ��ʶ����
    result = c_char_p(b"                              ")
    timeout = 10
    # ��֤���ļ�·��
    filename = file
    # һ��ʶ������������� YDM_SetAppInfo �� YDM_Login���ʺϽű�����
    captchaId = YDMApi.YDM_EasyDecodeByPath(username, password, appId, appKey, filename, codetype, timeout, result)
    print("һ��ʶ����֤��ID��%d��ʶ������%s" % (captchaId, result.value))
    return result.value

