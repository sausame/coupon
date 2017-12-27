#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import time
import traceback

from datetime import datetime
from special import Viewer
from qwd import QWD
from utils import reprDict, OutputPath, ThreadWritableObject

def run(configFile, shareFile, name, savefile, logFile):

    OutputPath.init(configFile)

    thread = ThreadWritableObject(configFile, name, logFile)
    thread.start()

    sys.stdout = thread
    sys.errout = thread # XXX: Actually, it does NOT work

    try:
        qwd = QWD(shareFile)

        viewer = Viewer(configFile, qwd)
        data = viewer.get()

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

    thread.quit()
    thread.join()

if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf8')

    if len(sys.argv) < 3:
        print 'Usage:\n\t', sys.argv[0], 'config-file share-config-file [save-file] [log-file]\n'
        exit()

    os.environ['TZ'] = 'Asia/Shanghai'
    time.tzset()

    name = os.path.basename(sys.argv[0])[:-3] # Remove ".py"
    configFile = os.path.realpath(sys.argv[1])
    shareFile = os.path.realpath(sys.argv[2])

    savefile = None
    logFile = None

    if len(sys.argv) > 3:
        savefile = sys.argv[3]

    if len(sys.argv) > 4:
        logFile = sys.argv[4]

    run(configFile, shareFile, name, savefile, logFile)

