#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import time
import traceback

from account import Account
from datetime import tzinfo, timedelta, datetime
from db import Database
from utils import OutputPath, ThreadWritableObject

def run(configFile, userId, name, inputPath, outputPath, loginConfigFile, logFile):

    OutputPath.init(configFile)

    thread = ThreadWritableObject(configFile, name, logFile)
    thread.start()

    sys.stdout = thread
    sys.errout = thread # XXX: Actually, it does NOT work

    try:
        db = Database(configFile, 'register')
        db.initialize()

        account = Account(db, userId)
        account.login(inputPath, outputPath, loginConfigFile)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print 'Error occurs at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        traceback.print_exc(file=sys.stdout)
    finally:
        try:
            if db is not None:
                db.quit()
        except:
            pass

    thread.quit()
    thread.join()

if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf8')

    if len(sys.argv) < 3:
        print 'Usage:\n\t', sys.argv[0], 'config-file user-id [login-config-file] [input-path] [output-path] [log-file]\n'
        exit()

    os.environ['TZ'] = 'Asia/Shanghai'
    time.tzset()

    name = os.path.basename(sys.argv[0])[:-3] # Remove ".py"
    configFile = os.path.realpath(sys.argv[1])
    userId = int(sys.argv[2])

    loginConfigFile = None
    inputPath = None
    outputPath = None
    logFile = None

    if len(sys.argv) > 3:
        inputPath = os.path.realpath(sys.argv[3])

    if len(sys.argv) > 4:
        outputPath = os.path.realpath(sys.argv[4])

    if len(sys.argv) > 5:
        loginConfigFile = os.path.realpath(sys.argv[5])

    if len(sys.argv) > 6:
        logFile = sys.argv[6]

    run(configFile, userId, name, inputPath, outputPath, loginConfigFile, logFile)

