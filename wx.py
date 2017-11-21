# -*- coding:utf-8 -*-

import random
import itchat
import time

from schedule import Schedule
from special import Searcher
from utils import getProperty, randomSleep, reprDict

class WX(Schedule):

    def __init__(self, configFile):

        Schedule.__init__(self, configFile)

        self.searcher = Searcher(configFile)

        self.configFile = configFile

    def login(self, exitCallback, uuid=None):

        def isLoginned(uuid):

            for count in range(10):

                status = int(itchat.check_login(uuid))

                if status is 200:
                    return True

                if status is 201:
                    print 'Wait for confirm in mobile #', count
                    randomSleep(1, 2)
                    continue

                print 'Error status:', status
                return False

            return False

        if uuid is None:

            statusFile = getProperty(self.configFile, 'wechat-status-file')
            itchat.auto_login(hotReload=True, statusStorageDir=statusFile)

        else:

            if not isLoginned(uuid):
                raise Exception('Failed to login with {}'.format(uuid))

            userInfo = itchat.web_init()

            itchat.show_mobile_login()
            itchat.get_friends(True)

            itchat.start_receiving(exitCallback)

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

    def search(self, friends, content):

        if not searcher.search(content):
            return

        for friend in friends:
            WX.sendTo(friend, searcher.plate, searcher.image)

