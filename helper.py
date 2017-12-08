#!/usr/bin/env python
# -*- coding:utf-8 -*-

import itchat
import os
import sys
import time
import traceback

from datetime import datetime
from wx import WX
from utils import OutputPath, ThreadWritableObject

def run(configFile, shareFile, name, uuid, logFile):

    wx = None

    @itchat.msg_register(itchat.content.TEXT)
    def text(msg):
        wx.text(msg)

    @itchat.msg_register(itchat.content.TEXT, isGroupChat = True)
    def textInGroup(msg):
        wx.textInGroup(msg)

    def quit():
        try:
            wx.quit()
        except:
            pass

    OutputPath.init(configFile)

    thread = ThreadWritableObject(configFile, name, logFile)
    thread.start()

    sys.stdout = thread
    sys.errout = thread # XXX: Actually, it does NOT work

    try:
        wx = WX(configFile, shareFile)
        wx.login(quit, uuid)
    except KeyboardInterrupt:
        pass
    except Exception, e:
        print 'Error occurs at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        traceback.print_exc(file=sys.stdout)
    finally:
        quit()

    thread.quit()
    thread.join()

if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf8')

    if len(sys.argv) < 3:
        print 'Usage:\n\t', sys.argv[0], 'config-file share-config-file [uuid] [log-file]\n'
        exit()

    os.environ['TZ'] = 'Asia/Shanghai'
    time.tzset()

    name = os.path.basename(sys.argv[0])[:-3] # Remove ".py"
    configFile = os.path.realpath(sys.argv[1])
    shareFile = os.path.realpath(sys.argv[2])

    uuid = None
    logFile = None

    if len(sys.argv) > 3:
        uuid = sys.argv[3]

    if len(sys.argv) > 4:
        logFile = sys.argv[4]

    run(configFile, shareFile, name, uuid, logFile)

