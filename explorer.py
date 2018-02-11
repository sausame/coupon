#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import time
import traceback

from datetime import datetime
from db import Database
from qwd import QWD
from search import SearchingKeyRegex
from special import Searcher
from utils import reprDict, OutputPath, ThreadWritableObject

def run(configFile, userId, name, content, savefile, logFile):

    OutputPath.init(configFile)

    thread = ThreadWritableObject(configFile, name, logFile)
    thread.start()

    sys.stdout = thread
    sys.errout = thread # XXX: Actually, it does NOT work

    try:
        key = SearchingKeyRegex.parse(content)

        if key is None:
            key = content

        print 'Searching "', key, '" from user', userId

        db = None
        qwd = None

        db = Database(configFile, 'register')
        db.initialize()

        qwd = QWD(db, userId)

        searcher = Searcher(configFile, qwd)
        data = searcher.explore(key)

        if savefile is not None:
            with open(savefile, 'w') as fp:
                fp.write(reprDict(data))
        else:
            print reprDict(data)

    except KeyboardInterrupt:
        pass
    except Exception, e:
        print 'Error occurs at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        traceback.print_exc(file=sys.stdout)
    finally:
        try:
            if qwd is not None:
                qwd.updateDb()

            if db is not None:
                db.quit()
        except:
            pass

    thread.quit()
    thread.join()

if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf-8')

    if len(sys.argv) < 5:
        print 'Usage:\n\t', sys.argv[0], 'config-file user-id content save-file [log-file]\n'
        exit()

    os.environ['TZ'] = 'Asia/Shanghai'
    time.tzset()

    name = os.path.basename(sys.argv[0])[:-3] # Remove ".py"
    configFile = os.path.realpath(sys.argv[1])
    userId = int(sys.argv[2])
    content = sys.argv[3]
    savefile = sys.argv[4]

    logFile = None

    if len(sys.argv) > 5:
        logFile = sys.argv[5]

    run(configFile, userId, name, content, savefile, logFile)

