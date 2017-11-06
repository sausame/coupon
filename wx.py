# -*- coding:utf-8 -*-

import random
import itchat
import time

from schedule import Schedule
from utils import getProperty, reprDict

class WX(Schedule):

    def __init__(self, configFile):

        Schedule.__init__(self, configFile)

        self.configFile = configFile

    def login(self):

        statusFile = getProperty(self.configFile, 'wechat-status-file')

        itchat.auto_login(hotReload=True, statusStorageDir=statusFile)

        self.me = itchat.search_friends()

        print self.me['NickName'], 'is working'

        self.watchFriends = list()
        names = getProperty(self.configFile, 'wechat-watch-friends').split(';')
        for name in names:
            friends = itchat.search_friends(name=name) 
            self.watchFriends.extend(friends)

        self.watchGroups = list()
        names = getProperty(self.configFile, 'wechat-watch-groups').split(';')
        for name in names:
            groups = itchat.search_chatrooms(name=name)
            self.watchGroups.extend(groups)

        itchat.run(blockThread=False) # Run in a new thread

        shareUrl = getProperty(self.configFile, 'share-url')
        self.setUrl(shareUrl)

        self.run()

    @staticmethod
    def sendTo(obj, plate, image):

        print '================================================================'
        print 'Send a message to', obj['NickName']

        interval = random.random() * 10
        time.sleep(interval)

        ret = obj.send(plate)

        print 'Result of text message:', ret['BaseResponse']['ErrMsg']
        print '----------------------------------------------------------------'
        print plate
        print '----------------------------------------------------------------'

        interval = random.random() * 10
        time.sleep(interval)

        ret = obj.send_image(image)
        print 'Result of', image, ':', ret['BaseResponse']['ErrMsg']

        print '================================================================'

    def text(self, msg):

        for friend in self.watchFriends:
            if msg['FromUserName'] == friend['UserName']:
                break
        else:
            return

        print '================================================================'
        print msg['User']['NickName'], 'sends a message:'
        print '----------------------------------------------------------------'
        print msg['Content']
        print '================================================================'

    def send(self, plate, image):

        for friend in self.watchFriends:
            WX.sendTo(friend, plate, image)

