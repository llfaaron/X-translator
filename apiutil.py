#-*- coding: UTF-8 -*-
import hashlib
import urllib
import urllib.request
import base64
import json
import time
import binascii

url_preffix='https://api.ai.qq.com/fcgi-bin/'

def setParams(array, key, value):
    array[key] = value

def genSignString(parser):
    uri_str = ''
    for key in sorted(parser.keys()):
        if key == 'app_key':
            continue
        if key == 'speech_chunk':
            uri_str += "%s=%s&" % (key, urllib.parse.quote(str(parser[key].decode()), safe=''))
            continue
        uri_str += "%s=%s&" % (key, urllib.parse.quote(str(parser[key]), safe = ''))
    sign_str = uri_str + 'app_key=' + parser['app_key']

    hash_md5 = hashlib.md5(sign_str.encode())
    return hash_md5.hexdigest().upper()


class AiPlat(object):
    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key
        self.data = {}

    def invoke(self, params,sign):

        self.url_data = urllib.parse.urlencode(params)
        # print(self.url_data)
        req = urllib.request.Request(self.url, self.url_data.encode())

        try:
            rsp = urllib.request.urlopen(req)
            str_rsp = rsp.read()
            dict_rsp = json.loads(str_rsp)
            return dict_rsp
        except urllib.request.URLError as e:
            dict_error = {}
            if hasattr(e, "code"):
                dict_error = {}
                dict_error['ret'] = -1
                dict_error['httpcode'] = e.code
                dict_error['msg'] = "sdk http post err"
                return dict_error
            if hasattr(e,"reason"):
                dict_error['msg'] = 'sdk http post err'
                dict_error['httpcode'] = -1
                dict_error['ret'] = -1
                return dict_error
        else:
            dict_error = {}
            dict_error['ret'] = -1
            dict_error['httpcode'] = -1
            dict_error['msg'] = "system error"
            return dict_error


    def getAaiWxAsrs(self, chunk, end_flag, format_id, seq):
        self.url = url_preffix + 'nlp/nlp_speechtranslate'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', str(time.time()))
        speech_chunk = base64.b64encode(chunk)
        setParams(self.data, 'speech_chunk', speech_chunk)
        setParams(self.data, 'end', end_flag)
        setParams(self.data, 'format', format_id)
        setParams(self.data, 'seq', seq)
        setParams(self.data, 'source', 'jp')
        setParams(self.data, 'target', 'zh')
        setParams(self.data, 'session_id', str(time.time()))
        sign_str = genSignString(self.data)
        setParams(self.data, 'sign', sign_str)

        return self.invoke(self.data,sign_str)