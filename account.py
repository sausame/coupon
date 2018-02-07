#!/usr/bin/env python
# -*- coding:utf-8 -*-

import base64
import json
import os
import requests
import sys
import time
import traceback

from datetime import tzinfo, timedelta, datetime
from imgkit import ImageKit
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from urlutils import JsonResult
from utils import displayImage, randomSleep, remove, reprDict, findElement, inputElement, OutputPath, getchar

class Inputter:

    def __init__(self, aId=None, inputPath=None, outputPath=None, retries=10):

        self.aId = aId

        self.inputPath = inputPath
        self.outputPath = outputPath

        self.retries = retries

        self.reset()

    def reset(self):

        self.content = None
        self.code = 1

        if self.inputPath is not None:
            remove(self.inputPath)

    def getInput(self, notice=None, msg=None, image=None, prompt=None, length=-1):

        if self.inputPath is not None:
            content = self.getInputFromFile(notice, msg, image, prompt, length)
        else:
            content = self.getInputFromStdin(notice, msg, image, prompt, length)

        if content is not None and isinstance(content, str):
            content = content.decode('utf-8', 'ignore')

        return content

    def getInputFromFile(self, notice, msg, image, prompt, length):

        with open(self.outputPath, 'w') as fp:

            content = dict()

            content['id'] = self.aId

            content['notice'] = notice
            content['message'] = msg

            content['image'] = None

            if image is not None:
                with open(image) as imageFp:
                    content['image'] = base64.b64encode(imageFp.read())

            content['prompt'] = prompt
            content['length'] = length

            content = JsonResult.create(content, self.code, prompt)

            fp.write(reprDict(content))

        for i in range(self.retries):

            time.sleep(1)

            try:
                with open(self.inputPath) as fp:

                    content = fp.read()
                    content = content.strip()

                    if ((length > 0 and len(content) is length) or (length < 0 and len(content) > 0)) \
                        and self.content != content:

                        self.content = content
                        self.code += 1 # Increase code

                        break

            except IOError as e:
                pass
        else:
            return None

        return self.content

    def getInputFromStdin(self, notice, msg, image, prompt, length):

        for i in range(self.retries):

            displayImage(image)

            print 'Notice:', notice
            print 'Message:', msg

            content = raw_input('{}:\n'.format(prompt))
            content = content.strip()

            if (length is not 0 and len(content) is length) or (length is 0 and len(content) > 0):
                self.content = content
                break
        else:
            return None

        return self.content

class Account:

    def __init__(self, db, userId):

        self.db = db
        self.userId = userId

        self.initUserConfig()

    def initUserConfig(self):

        sql = ''' SELECT
                      config
                  FROM
                      `configs`
                  WHERE
                      userId = {} '''.format(self.userId)

        result = self.db.query(sql)

        config = None

        for row in result:
            config = row['config']

        if config is None:
            raise Exception('Config is invalid for user {}'.format(self.userId))

        try:
            configObj = json.loads(config.decode('utf-8', 'ignore'))
        except ValueError as e:
            raise Exception('Config is invalid for user {}'.format(self.userId))

        ## Login
        obj = configObj.pop('login')

        self.username = obj.pop('username')
        password = obj.pop('password')
        self.password = base64.b64decode(password)

        self.image = OutputPath.getAuthPath('user_{}'.format(self.userId))
        self.originalImage = OutputPath.getAuthPath('user_{}_original'.format(self.userId))

    def saveScreenshot(self, driver, screenshotPath):

        driver.save_screenshot(self.originalImage)
        ImageKit.resize(screenshotPath, self.originalImage, newSize=(400, 300))

    def login(self, screenshotPath=None, inputPath=None, outputPath=None, config='templates/login.json', retries=10):

        result = JsonResult.error()

        if config is None:
            config='templates/login.json'

        with open(config) as fp:
            content = fp.read()

        try:
            configObj = json.loads(content.decode('utf-8', 'ignore'))
        except ValueError as e:
            raise Exception('{} is not valid config file for user {}.'.format(config, self.userId))

        obj = configObj.pop('config')

        driverType = obj.pop('driver')

        loginUrl = obj.pop('login-url')
        verificationUrl = obj.pop('verification-url')

        display = Display(visible=0, size=(800, 600))
        display.start()

        if 'firefox' == driverType:

            # https://github.com/mozilla/geckodriver/releases
            driver = webdriver.Firefox()

        else: # Chrome

            # https://chromedriver.storage.googleapis.com/index.html
            driver = webdriver.Chrome()

        try:

            driver.get(loginUrl)
            driver.set_script_timeout(10)

            # Username and password
            randomSleep(1, 2)
            inputElement(driver.find_element_by_id('username'), self.username)

            randomSleep(1, 2)
            inputElement(driver.find_element_by_id('password'), self.password)

            self.saveScreenshot(driver, screenshotPath);

            # Submit
            buttonElement = driver.find_element_by_id('loginBtn')

            randomSleep(1, 2)
            buttonElement.click()

            authCodeInputter = Inputter('AuthCode', inputPath, outputPath)
            verificationInputter = Inputter('Verification', inputPath, outputPath)

            for i in range(retries):

                if loginUrl != driver.current_url:
                    break

                time.sleep(1)

                self.saveScreenshot(driver, screenshotPath);

                error = self.getLoginError(driver)

                if error is not None:

                    if u'账号或密码不正确' in error:
                        return JsonResult.error(message=error)

                    if u'验证码' not in error:
                        return JsonResult.error(message=error)

                if self.inputAuthCode(driver, authCodeInputter, error):
                    continue

                # Need code
                if self.isPhoneCodeNeeded(driver):
                    continue

                # Verification
                if self.verify(driver, verificationInputter):
                    continue
            else:
                raise Exception('Unable to login for user {} in {}.'.format(self.userId, loginUrl))

            codeInputter = Inputter('Code', inputPath, outputPath)

            for i in range(retries):

                if verificationUrl != driver.current_url:
                    break

                time.sleep(1)

                self.saveScreenshot(driver, screenshotPath);

                self.inputPhoneCode(driver, codeInputter)
            else:
                raise Exception('Unable to login for user {} in {}.'.format(self.userId, verificationUrl))

            time.sleep(3)

            self.updateDb(driver)

            result = JsonResult.succeed()

        except KeyboardInterrupt:
            pass
        except Exception as e:
            print 'Error occurs at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            traceback.print_exc(file=sys.stdout)
        finally:
            driver.quit()

            if display is not None:
                display.stop()

        time.sleep(1)

        return result

    def getLoginError(self, driver):

        noticeName = '//div[@class="notice"]'

        element = findElement(driver, noticeName)

        if element is None or not element.is_displayed() or not element.is_enabled():
            return None

        notice = element.text

        if '&nbsp;' == notice:
            return None

        return notice

    def inputAuthCode(self, driver, inputter, notice):

        divAuthCodeId = 'input-code'
        divImgVerfiyName = '//div[@class="txt-imgverify"]'
        imgAutoCodeId = 'imgCode'
        inputAuthCodeId = 'code'
        loginButtonId = 'loginBtn'

        msg = None

        element = findElement(driver, divAuthCodeId)

        if element is None or not element.is_displayed() or not element.is_enabled():
            return False

        print 'Auth code is needed.'

        element = findElement(driver, divImgVerfiyName)

        if element is not None:
            msg = element.text

        element = findElement(driver, imgAutoCodeId)

        if element is None:
            return True

        ImageKit.saveCapture(driver, element, self.image)

        element = findElement(driver, inputAuthCodeId)

        if element is None:
            return False

        prompt = element.get_attribute('placeholder')

        content = inputter.getInput(notice, msg, self.image, prompt, 4)

        if content is None:
            return True

        element.clear()
        element.send_keys(content);

        print 'Auth code is sent.'

        time.sleep(1)

        element = findElement(driver, loginButtonId)
        element.click()

        time.sleep(3) # Sleep a little longer

        return True

    def isPhoneCodeNeeded(self, driver):

        continueButtonName = '//a[@class="btn-pop btn-continue"]'

        element = findElement(driver, continueButtonName)

        if element is None or not element.is_displayed() or not element.is_enabled():
            return False

        element.click()

        time.sleep(3) # Sleep a little longer

        return True

    def inputPhoneCode(self, driver, inputter):

        tipsName = '//div[@class="item item-tips"]'
        retransmitButtonName = '//a[@class="btn-retransmit"]'
        inputName = '//input[@class="txt-input txt-phone"]'
        loginName = '//a[@class="btn-login"]'

        print 'Phone code is needed ...'

        # Notice
        element = findElement(driver, tipsName) 

        if element is not None:
            notice = element.text

        element = findElement(driver, retransmitButtonName) 

        if element is not None:
            element.click()
            time.sleep(3)
            return # Wait for next code

        element = findElement(driver, inputName)

        if element is not None:

            prompt = element.get_attribute('placeholder')

            content = inputter.getInput(notice, '', self.image, prompt, 6)

            if content is None:
                return

            element = findElement(driver, inputName)

            element.send_keys(Keys.CONTROL, 'a')
            element.send_keys(Keys.DELETE);
            element.send_keys(content);

            print 'Phone code is sent.'

            time.sleep(1)

            element = findElement(driver, loginName)
            element.click()

            time.sleep(3)

    def verify(self, driver, inputter):

        verifyBodyName = '//div[@class="verify-body"]'
        verifyMsgName = '//p[@class="verify-msg"]'
        verifyNoticeName = '//div[@class="verify-notice"]'
        verifyInputName = '//input[@class="verify-input"]'
        verifyContinueName = '//a[@class="verify-continue"]'

        time.sleep(1)

        # Verification

        element = findElement(driver, verifyBodyName)

        if element is None or not element.is_displayed() or not element.is_enabled():
            return False

        print 'Verification is needed ...'

        ImageKit.saveCapture(driver, element, self.image)

        element = findElement(driver, verifyNoticeName)

        if element is not None:
            notice = element.text
        else:
            notice = None

        element = findElement(driver, verifyMsgName)

        if element is not None:
            msg = element.text
        else:
            msg = None

        element = findElement(driver, verifyInputName)

        if element is not None:

            prompt = element.get_attribute('placeholder')

            content = inputter.getInput(notice, msg, self.image, prompt)

            if content is None:
                return

            element.send_keys(content)

            print 'Verification code is sent.'

            time.sleep(2)

            element = findElement(driver, verifyContinueName)

            if element is not None:

                element.click()

                time.sleep(3) # Sleep a little longer

        return True

    def updateDb(self, driver):

        # Redirect to wqs
        time.sleep(1)

        # Save as type of cookie for requests
        cookies = dict()
        for cookie in driver.get_cookies():

            k = cookie['name']
            v = cookie['value']

            cookies[k] = v

        entryCookies = reprDict(cookies)

        sql = ''' UPDATE
                      `configs`
                  SET
                      `entryCookies`= '{}'
                  WHERE
                      `userId` = {} '''.format(entryCookies, self.userId)

        self.db.query(sql)

