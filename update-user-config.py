#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import time
import traceback

from datetime import datetime
from db import Database
from qwd import QWD
from utils import OutputPath, ThreadWritableObject

def run(configFile, userId, name, logFile):

    OutputPath.init(configFile)

    thread = ThreadWritableObject(configFile, name, logFile)
    thread.start()

    sys.stdout = thread
    sys.errout = thread # XXX: Actually, it does NOT work

    try:
        db = None
        qwd = None

        db = Database(configFile, 'register')
        db.initialize()

        qwd = QWD(db, userId)
        qwd.updateDb(force=True)

    except KeyboardInterrupt:
        pass
    except Exception, e:
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
        print 'Usage:\n\t', sys.argv[0], 'config-file user-id [log-file]\n'
        exit()

    os.environ['TZ'] = 'Asia/Shanghai'
    time.tzset()

    name = os.path.basename(sys.argv[0])[:-3] # Remove ".py"
    configFile = os.path.realpath(sys.argv[1])
    userId = int(sys.argv[2])

    logFile = None

    if len(sys.argv) > 3:
        logFile = sys.argv[3]

    run(configFile, userId, name, logFile)

