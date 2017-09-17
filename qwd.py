# -*- coding:utf-8 -*-

import codecs
import json
import random
import re
import requests
import time

from utils import getMatchString, getProperty

class CPS:

    def __init__(self):
        pass

    def login(self):
        pass

    def getSkuId(self):
        pass

class QWD:

    def __init__(self, configFile):

        self.configFile = configFile

        self.appid = getProperty(self.configFile, 'cps-qwd-appid')
        self.ctype = getProperty(self.configFile, 'cps-qwd-ctype')
        self.ie = getProperty(self.configFile, 'cps-qwd-ie')
        self.p = getProperty(self.configFile, 'cps-qwd-p')
        self.qwd_chn = getProperty(self.configFile, 'cps-qwd-qwd_chn')
        self.qwd_schn = getProperty(self.configFile, 'cps-qwd-qwd_schn')
        self.login_mode = getProperty(self.configFile, 'cps-qwd-login_mode')

        self.uuid = getProperty(self.configFile, 'cps-qwd-uuid')

        self.pin = getProperty(self.configFile, 'cps-qwd-pin')
        self.tgt = getProperty(self.configFile, 'cps-qwd-tgt')

        self.shareUrl = getProperty(self.configFile, 'cps-qwd-share-url')
        self.imageUrl = getProperty(self.configFile, 'cps-qwd-share-image-url')

        self.shareCookie = getProperty(self.configFile, 'cps-qwd-share-cookie')

        self.userAgent = getProperty(self.configFile, 'cps-qwd-http-user-agent')

        #XXX: Can NOT use session to store cookie because these fields are not
        #     valid http cookie.
        self.cookies = dict()

    def login(self):

        # Url
        url = getProperty(self.configFile, 'cps-qwd-login-url')

        # Data
        data = {'appid': self.appid,
                'ctype': self.ctype,
                'ie': self.ie,
                'p': self.p,
                'pin': self.pin,
                'tgt': self.tgt,
                'uuid': self.uuid}

        # Request
        r = requests.post(url, data=data)
        response = r.content
        #print url, data, r.cookies, response

        with open('a.json', 'w+') as fp:
            fp.write(response)

        obj = json.loads(response.decode('utf-8', 'ignore'))

        # Login status
        errCode = int(obj.pop('errCode'))

        if errCode is not 0:
            print 'Failed to login to', url, ':\n', response
            return False

        print('Logined to qwd.jd.com')

        obj = obj.pop('loginInfo')

        self.apptoken = obj.pop('apptoken')
        self.pinType = obj.pop('pinType')
        self.jxjpin = obj.pop('jxjpin')

        self.cookies = {'app_id': self.appid,
                'apptoken': self.apptoken,
                'client_type': self.ctype,
                'jxjpin': self.jxjpin,
                'pinType': self.pinType,
                'tgt': self.tgt,
                'qwd_chn': self.qwd_chn,
                'qwd_schn': self.qwd_schn,
                'login_mode': self.login_mode}

        return True

    @staticmethod
    def isValidShareUrl(url):

        pattern = r'(https://union-click\.jd\.com/jdc\?d=\w+)'

        return re.match(pattern, url) is not None

    def getShareUrl(self, skuid):

        url = self.shareUrl.format(skuid)

        headers = {'User-Agent': self.userAgent}

        r = requests.get(url, cookies=self.cookies, headers=headers)

        if 200 != r.status_code:
            print 'Unable to get sharing URL for "', skuid, '" with an error (', r.status_code, '):\n', r.text
            return None

        content = r.content.replace('\n', '')
        data = getMatchString(content, r'itemshare\((.*?)\)')

        obj = json.loads(data.decode('utf-8', 'ignore'))
        retCode = int(obj.pop('retCode'))

        if retCode is not 0:
            print 'Unable to get sharing URL for "', skuid, '" with an error (', r.status_code, '):\n', r.text

            # XXX: Relogin, but let this message failed because of less complicated logistic
            self.login()
            return None

        return obj.pop('skuurl')

    def getSkuId(self, url):

        headers = {'User-Agent': self.userAgent}
        r = requests.get(url, headers=headers)

        if 200 != r.status_code:
            print 'Unable to get long URL for "', skuid, '" with an error (', r.status_code, '):\n', r.text
            return None

        url = getMatchString(r.content, r"hrl='(.*?)'")
        #print 'Long url:', url

        headers = {'User-Agent': self.userAgent}
        r = requests.get(url, headers=headers)

        if 200 != r.status_code:
            print 'Unable to get information page for "', skuid, '" with an error (', r.status_code, '):\n', r.text
            return None

        data = getMatchString(r.content, r'window._itemOnly = (.*?);')
        #print data

        obj = json.loads(data.decode('utf-8', 'ignore'))
        obj = obj.pop('item')

        skuId = obj.pop('areaSkuId')

        return skuId

    def getImageUrl(self, skuid):

        url = self.imageUrl.format(random.randint(1000000000, 9999999999), skuid)
        headers = {'User-Agent': self.userAgent}

        r = requests.get(url, headers=headers)

        if 200 != r.status_code:
            print 'Unable to get image URL for "', skuid, '" with an error (', r.status_code, '):\n', r.text
            return None

        img = getMatchString(r.content, r'skuimgurl":"(https://img\S+)",')

        return img

    def saveImage(self, path, skuid):

        url = self.getImageUrl(skuid)
        if url is None:
            return False

        r = requests.get(url)

        if 200 != r.status_code:
            print 'Unable to get image data for "', skuid, '" with an error (', r.status_code, '):\n', r.text
            return False

        with codecs.open(path, 'wb') as fp:
            fp.write(r.content)

        return True

