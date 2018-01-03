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

def run(configFile, userConfigFile, name, shareFile, index, savefile, logFile):

    OutputPath.init(configFile)

    thread = ThreadWritableObject(configFile, name, logFile)
    thread.start()

    sys.stdout = thread
    sys.errout = thread # XXX: Actually, it does NOT work

    try:
        qwd = QWD(userConfigFile)

        viewer = Viewer(configFile, qwd)
        data = viewer.get(shareFile, index)

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

    if len(sys.argv) < 5:
        print 'Usage:\n\t', sys.argv[0], 'config-file user-config-file share-file index [save-file] [log-file]\n'
        exit()

    os.environ['TZ'] = 'Asia/Shanghai'
    time.tzset()

    name = os.path.basename(sys.argv[0])[:-3] # Remove ".py"
    configFile = os.path.realpath(sys.argv[1])
    userConfigFile = os.path.realpath(sys.argv[2])
    shareFile = os.path.realpath(sys.argv[3])
    index = int(sys.argv[4])

    savefile = None
    logFile = None

    if len(sys.argv) > 5:
        savefile = sys.argv[5]

    if len(sys.argv) > 6:
        logFile = sys.argv[6]

    run(configFile, userConfigFile, name, shareFile, index, savefile, logFile)

