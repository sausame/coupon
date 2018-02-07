#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import time
import traceback

from account import Account
from datetime import tzinfo, timedelta, datetime
from db import Database
from urlutils import JsonResult
from utils import reprDict, OutputPath, ThreadWritableObject

def run(configFile, userId, name, screenshotPath, inputPath, outputPath, loginConfigFile, logFile):

    OutputPath.init(configFile)

    thread = ThreadWritableObject(configFile, name, logFile)
    thread.start()

    sys.stdout = thread
    sys.errout = thread # XXX: Actually, it does NOT work

    result = JsonResult.error()

    try:
        db = Database(configFile, 'register')
        db.initialize()

        account = Account(db, userId)
        result = account.login(screenshotPath, inputPath, outputPath, loginConfigFile)

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

    try:
        if outputPath is not None:
            with open(outputPath, 'w') as fp:
                fp.write(reprDict(result))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print 'Error occurs at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        traceback.print_exc(file=sys.stdout)

    thread.quit()
    thread.join()

if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf8')

    if len(sys.argv) < 3:
        print 'Usage:\n\t', sys.argv[0], 'config-file user-id [screenshot-path] [input-path] [output-path] [login-config-file] [log-file]\n'
        exit()

    os.environ['TZ'] = 'Asia/Shanghai'
    time.tzset()

    name = os.path.basename(sys.argv[0])[:-3] # Remove ".py"
    configFile = os.path.realpath(sys.argv[1])
    userId = int(sys.argv[2])

    screenshotPath = None
    inputPath = None
    outputPath = None
    loginConfigFile = None
    logFile = None

    if len(sys.argv) > 3:
        screenshotPath = os.path.realpath(sys.argv[3])

    if len(sys.argv) > 4:
        inputPath = os.path.realpath(sys.argv[4])

    if len(sys.argv) > 5:
        outputPath = os.path.realpath(sys.argv[5])

    if len(sys.argv) > 6:
        loginConfigFile = os.path.realpath(sys.argv[6])

    if len(sys.argv) > 7:
        logFile = sys.argv[7]

    run(configFile, userId, name, screenshotPath, inputPath, outputPath, loginConfigFile, logFile)

