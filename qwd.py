# -*- coding:utf-8 -*-

import base64
import codecs
import json
import os
import random
import re
import requests
import time

from imgkit import ImageKit
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from utils import chmod, getMatchString, getProperty, inputElement, randomSleep, reprDict, OutputPath

class CPS:

    def __init__(self):
        pass

    def login(self):
        pass

    def getSkuId(self):
        pass

class QWD:

    def __init__(self, db=None, userId=None):

        self.initShareConfig()
        self.initUserConfig(db, userId)

        self.reset()

    def initShareConfig(self):

        with open('templates/share.json', 'r') as fp:
            content = fp.read()

        try:
            configObj = json.loads(content.decode('utf-8', 'ignore'))
        except ValueError as e:
            raise Exception('{} is not valid config file.'.format(configFile))

        loginObj = configObj.pop('login')

        ## Login
        self.loginMethod = loginObj.pop('login-method')

        # Plogin
        ploginObj = loginObj.pop('plogin')

        self.ploginType = ploginObj.pop('plogin-type')
        self.ploginUrl = ploginObj.pop('plogin-url')
        self.ploginSeccessfulUrl = ploginObj.pop('plogin-seccessful-url')
        self.wqUrl = ploginObj.pop('wq-url')
        self.wqsUrl = ploginObj.pop('wqs-url')

        # Login
        loginObj = loginObj.pop('login')

        self.loginUrl = loginObj.pop('login-url')
        self.appid = loginObj.pop('appid')
        self.ie = loginObj.pop('ie')
        self.p = loginObj.pop('p')
        self.qwd_chn = loginObj.pop('qwd_chn')
        self.qwd_schn = loginObj.pop('qwd_schn')
        self.login_mode = loginObj.pop('login_mode')

        ## Search
        searchObj = configObj.pop('search')

        self.searchItemUrl = searchObj.pop('search-item-url')
        self.pageindex = searchObj.pop('pageindex')
        self.pagesize = searchObj.pop('pagesize')
        self.uniquespu = searchObj.pop('uniquespu')
        self.storestatus = searchObj.pop('storestatus')
        self.comsrate = searchObj.pop('comsrate')
        self.sortBy = searchObj.pop('sortby').split(';')
        self.order = searchObj.pop('order').split(';')
        self.coupon = searchObj.pop('coupon')
        self.pwprice = searchObj.pop('pwprice')
        self.delivery = searchObj.pop('delivery')

        ## Share
        shareObj = configObj.pop('share')

        self.shareUrl = shareObj.pop('share-url')

        ## Common
        commonObj = configObj.pop('common')

        self.userAgent = commonObj.pop('http-user-agent')

    def initUserConfig(self, db, userId):

        if db is None or userId is None:
            return

        self.db = db
        self.userId = userId

        sql = ''' SELECT
                      config, entryCookies, keyCookies
                  FROM
                      `configs`
                  WHERE
                      userId = {}'''.format(self.userId)

        result = self.db.query(sql)

        config = None

        for row in result:
            config = row['config']
            self.entryCookies = row['entryCookies']
            self.keyCookies = row['keyCookies']

        if config is None:
            return

        try:
            configObj = json.loads(config.decode('utf-8', 'ignore'))
        except ValueError as e:
            raise Exception('Config is invalid for user {}'.format(self.userId))

        ## User
        userObj = configObj.pop('user')

        # Plogin
        ploginObj = userObj.pop('plogin')

        self.username = ploginObj.pop('username')
        password = ploginObj.pop('password')
        self.password = base64.b64decode(password)

        # Login
        loginObj = userObj.pop('login')

        self.pin = loginObj.pop('pin')
        self.tgt = loginObj.pop('tgt')

        self.ctype = loginObj.pop('ctype')
        self.uuid = loginObj.pop('uuid')

    def reset(self):

        self.apptoken = None
        self.pinType = None
        self.jxjpin = None

        #XXX: Can NOT use session to store cookie because these fields are not
        #     valid http cookie.
        self.cookies = dict()

        self.pCookies = None

        self.dbUpdated = False

    def login(self):

        if self.apptoken is not None:
            return True

        # Data
        data = {'appid': self.appid,
                'ctype': self.ctype,
                'ie': self.ie,
                'p': self.p,
                'pin': self.pin,
                'tgt': self.tgt,
                'uuid': self.uuid}

        # Request
        r = requests.post(self.loginUrl, data=data)
        response = r.content

        obj = json.loads(response.decode('utf-8', 'ignore'))

        # Login status
        errCode = int(obj.pop('errCode'))

        if errCode is not 0:
            print 'Failed to login to', self.loginUrl, ':\n', response
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

        for retries in range(3):

            if retries is not 0:
                time.sleep(1)

            if self.loginMethod is 1:

                if not self.plogin(retries):
                    continue

                cookies = self.pCookies

            else:
                if not self.login():
                    continue

                cookies = self.cookies

            try:
                r = requests.get(url, cookies=cookies, headers=headers)
            except Exception as e: 
                print 'Unable to get sharing URL for "', skuid, '" with an error:\n', e
                continue

            if 200 != r.status_code:
                print 'Unable to get sharing URL for "', skuid, '" with an error (', r.status_code, '):\n', r.text
                continue

            content = r.content.replace('\n', '')
            data = getMatchString(content, r'itemshare\((.*?)\)')

            obj = json.loads(data.decode('utf-8', 'ignore'))
            retCode = int(obj.pop('retCode'))

            if retCode is not 0:
                print 'Unable to get sharing URL for "', skuid, '" with an error (', r.status_code, '):\n', r.text
                continue

            return obj.pop('skuurl')

        # XXX: Reset but let this message failed because of less complicated logistic. It will re-login
        #      when call the function again.
        self.reset()

        return None

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

    # cut-type: 0, none; 1, coupon; 2, discount
    # prices: lowPrice, highPrice
    # sort by: 0, none; 1, wechat_price; 2, total_qtty; 3, good_comments
    # order: 0, asc; 1, desc;
    # delivery: 0, none; 1, jd delivery
    def search(self, key, cutType=0, price=None, sortByType=0, orderType=0, deliveryType=0):

        def formatPrice(low, high):
            if high is 0: 
                return '0-00'
            return '{}-{}'.format(low, high)

        payload = {'g_tk': random.randint(1000000000, 9999999999),
                'pageindex': self.pageindex,
                'pagesize': self.pagesize,
                'uniquespu': self.uniquespu,
                'storestatus': self.storestatus,
                'ie': self.ie,
                '_': int(time.time() * 1000)}

        # Commission Rate
        commissionRateData = {'comsrate': self.comsrate}
        payload.update(commissionRateData)

        # Key
        payload.update({'key': key, 'text': key})

        # Cut type
        if cutType is 1:
            payload.update({'coupon': self.coupon})
        elif cutType is 2:
            payload.update({'pwprice': self.pwprice})

        # Delivery
        if deliveryType is 1:
            payload.update({'delivery': self.delivery})

        # Price
        if price is not None and isinstance(price, tuple):
            payload.update({'wprice': formatPrice(price[0], price[1])})

        # Sort by
        if sortByType is not 0:

            sortByType -= 1

            payload.update({'sortby': self.sortBy[sortByType]})
            # Order
            payload.update({'order': self.order[orderType]})

        # Headers
        headers = {'User-Agent': self.userAgent}

        print 'Searching remotely with:', payload

        try:
            r = requests.get(self.searchItemUrl, params=payload, headers=headers)
        except Exception as e: 
            print 'Unable to search "', key, '" with price', price, ' because of an error:\n', e
            return None

        if 200 != r.status_code:
            print 'Unable to search "', key, '" with price', price, ' because of an error (', r.status_code, '):\n', r.text
            return None

        obj = json.loads(r.content.decode('utf-8', 'ignore'))
        errCode = int(obj.pop('errCode'))

        if errCode is not 0:
            print 'Wrong error code:', errCode
            return None

        return obj.pop('sku')

    def getImageUrl(self, skuid):

        skus = self.search(skuid)

        if skus is None:
            print 'No sku'
            return None

        for sku in skus:
            if sku['skuid'] == str(skuid):
                return sku['skuimgurl']

        return None

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

        chmod(path)

        return True

    def getBrowserError(self, browser):

        wait = WebDriverWait(browser, 3)
      
        try:
            page_loaded = wait.until_not(lambda browser: browser.current_url == self.ploginUrl)
            return None
        except Exception as e:
            pass

        noticeElement = browser.find_element_by_xpath('//div[@class="notice"]')
        return browser.execute_script("return arguments[0].innerHTML", noticeElement)

    def plogin(self, retries=0):

        def isValidAuthCode(code):

            if code is None or len(code) != 4:
                return False

            for c in code:

                if c.isdigit():
                    continue

                if c.isalpha():
                    continue

                # Wrong word
                return False

            return True

        if self.pCookies is not None:
            return True

        if retries is 0:
            pass
        elif retries is 1:
            self.keyCookies = None
        elif retries is 2:
            self.entryCookies = None
        else:
            return False

        cookies = None

        if self.entryCookies is not None:

            try:
                cookies = json.loads(self.entryCookies.decode('utf-8', 'ignore'))
            except ValueError as e:
                pass

        if cookies is None:

            if 'firefox' == self.ploginType:

                # https://github.com/mozilla/geckodriver/releases
                browser = webdriver.Firefox()

            else: # Chrome

                # https://chromedriver.storage.googleapis.com/index.html
                browser = webdriver.Chrome()

            try:
                # Plogin
                browser.get(self.ploginUrl)

                # Login by username and password

                # Username and password
                randomSleep(1, 2)
                inputElement(browser.find_element_by_id('username'), self.username)

                randomSleep(1, 2)
                inputElement(browser.find_element_by_id('password'), self.password)

                # Submit
                buttonElement = browser.find_element_by_id('loginBtn')

                # Code
                codeElement = browser.find_element_by_id('code')
                imageElement = browser.find_element_by_id('imgCode')

                times = 0

                if codeElement.is_displayed():

                    while codeElement.is_displayed() and times < 50:

                        times += 1

                        # Image to text
                        path = OutputPath.getAuthPath(self.username)

                        ImageKit.saveCapture(browser, imageElement, path)

                        code = ImageKit.getText(path)

                        codeElement.send_keys(code)

                        if not isValidAuthCode(code):

                            # Refresh auth code
                            randomSleep(0.5, 1)
                            imageElement.click()

                            # Wait for updating auth code 
                            randomSleep(1, 2)
                            codeElement.clear()

                            continue

                        # Submit
                        randomSleep(1, 2)
                        buttonElement.click()

                        error = self.getBrowserError(browser)

                        if error is None:
                            print 'Succeed after', times, 'tries.'
                            break

                        if u'验证码' not in error:
                            raise Exception('Unable to login for "{}": {}'.format(self.userId, error))

                        randomSleep(1, 2)
                        codeElement.clear()
                        randomSleep(1, 2)

                    else:
                        raise Exception('Unable to login for "{}"'.format(self.userId))

                else:
                    # Submit
                    randomSleep(1, 2)
                    buttonElement.click()

                    wait = WebDriverWait(browser, 3)
                  
                    error = self.getBrowserError(browser)

                    if error is not None:
                        raise Exception('Unable to login for "{}": {}'.format(self.userId, error))

                print 'Loginned for', self.userId

                # Redirect to wqs
                time.sleep(1)

                # Save as type of cookie for requests
                cookies = dict()
                for cookie in browser.get_cookies():

                    k = cookie['name']
                    v = cookie['value']

                    cookies[k] = v

                self.dbUpdated = True
                self.entryCookies = reprDict(cookies)

            except Exception as e:
                print 'Unable to get entry cookie with an error:\n', e
                return False
            finally:
                browser.quit()

        # Update pCookies
        self.pCookies = cookies

        cookies = None

        if self.keyCookies is not None:

            try:
                cookies = json.loads(self.keyCookies.decode('utf-8', 'ignore'))
            except ValueError as e:
                pass

        if cookies is None:

            try:
                # Headers
                headers = {'User-Agent': self.userAgent}

                params = {'rurl': self.wqsUrl}

                r = requests.get(self.wqUrl, params=params, cookies=self.pCookies, headers=headers, allow_redirects=False)
            except Exception as e: 
                print 'Unable to get key cookie with an error:\n', e
                return False

            cookies = dict()
            for cookie in r.cookies:
                cookies[cookie.name] = cookie.value

            self.dbUpdated = True
            self.keyCookies = reprDict(cookies)

        # Update pCookies
        self.pCookies.update(cookies)

        return True

    def updateDb(self):

        if not self.dbUpdated:
            return

        self.dbUpdated = False

        sql = ''' UPDATE
                      `configs`
                  SET
                      `entryCookies`= '{}',
                      `keyCookies`= '{}'
                  WHERE
                      `userId` = {} '''.format(self.entryCookies, self.keyCookies, self.userId)

        self.db.query(sql)

