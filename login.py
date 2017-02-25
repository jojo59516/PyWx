# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import re
import time
from io import BytesIO
from threading import Timer

import requests
from PIL import Image

def get_uuid():
    '''
    获取登陆二维码
    '''
    current_time = int(time.time()) #当前时间
    url = r'https://login.wx.qq.com/jslogin'
    params = {
        r'appid': r'wx782c26e4c19acffb',
        r'redirect_uri': r'https%3A%2F%2Fwx.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage',
        r'fun': r'new',
        r'lang': r'zh_CN',
        r'_': str(current_time)
    }
    r = requests.get(url, params = params)
    if r.status_code != requests.codes.ok:
        print("Cannot get QR code!")
        return None
    uuid = re.search(r'(?<=").*?(?=")', r.content.decode('utf-8')).group() #从response的content中截取uuid
    return uuid

def get_QRcode(uuid):
    #获取二维码
    url = r'https://login.weixin.qq.com/qrcode/' + uuid
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        print("Cannot get QR code!")
        return None
    qrcode_img = Image.open(BytesIO(r.content)) #requests会自动解码base64
    qrcode_img.save('QRcode.png')

    #显示二维码
    os.system('QRcode.png')

    return qrcode_img

def user_scanned_QRcode(uuid):
    current_time = int(time.time())
    url = r'https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login'
    params = {
        r'loginicon': r'true',
        r'uuid': uuid,
        r'tip': r'0',
        r'r': r'-1918576234',
        r'_': str(current_time) #当前时间
    }
    r = requests.get(url, params = params)
    if r.status_code != requests.codes.ok:
        print("Cannot get QR code!")
        return None
    
    window_redirect_uri = re.search(r'(?<=window\.redirect_uri=).+(?=;)', r.content.decode('utf-8')) #获取windows.redirect_uri的值，即重定向url
    if window_redirect_uri: #用户已经确认登陆
        return window_redirect_uri.group()
    window_code = re.search(r'(?<=window\.code=)\d+(?=;)', r.content.decode('utf-8')) #获取windows.code的值，即状态码
    if window_code: #用户已经扫描但未确认登录或未扫描
        return int(window_code.group())

    return None

def polling(interval, func, args = None):
    t = Timer(interval, func, args = args)
    t.start()
    return t

if __name__ == '__main__':
    uuid = get_uuid()

    get_QRcode(uuid)
    
    print("请使用手机扫描二维码以登录")
    ret_code = user_scanned_QRcode(uuid)
    while ret_code and isinstance(ret_code, int):
        if ret_code == 201:
            print("已扫描，等待确认...")
        else:
            pass
        time.sleep(1)
        ret_code = user_scanned_QRcode(uuid)
    else:
        if ret_code:
            print("已确认，登录中...")