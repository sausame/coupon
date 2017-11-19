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

def run(configFile, name, qrPath):

    wx = None

    @itchat.msg_register(itchat.content.TEXT)
    def text(msg):
        wx.text(msg)

    OutputPath.init(configFile)

    thread = ThreadWritableObject(configFile, name)
    thread.start()

    sys.stdout = thread
    sys.errout = thread # XXX: Actually, it does NOT work

    try:
        wx = WX(configFile)
        wx.login(qrPath)
    except KeyboardInterrupt:
        pass
    except Exception, e:
        print 'Error occurs at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        traceback.print_exc(file=sys.stdout)
    finally:
        try:
            wx.quit()
        except:
            pass

    thread.quit()
    thread.join()

if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf8')

    if len(sys.argv) < 2:
        print 'Usage:\n\t', sys.argv[0], 'config-file [qr-path]\n'
        exit()

    os.environ['TZ'] = 'Asia/Shanghai'
    time.tzset()

    name = os.path.basename(sys.argv[0])[:-3] # Remove ".py"
    configFile = sys.argv[1]
    qrPath = sys.argv[2]

    run(configFile, name, qrPath)

