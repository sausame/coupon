#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import traceback

from base import SpecialFormatter
from db import Database
from evaluation import Evaluation
from qwd import QWD
from utils import getchar, runCommand

def run(configfile, key, price=None):

    try:

        db = Database(configFile, 'specials')
        db.initialize()

        evaluation = Evaluation(configFile, db)

        if price is None:
            specialList = evaluation.smartSearch(key)
        else:
            specialList = list()

            localList = evaluation.search(key, price)
            if localList is not None:
                specialList.extend(localList)

            remoteList = evaluation.explore(key, price)
            if remoteList is not None:
                specialList.extend(remoteList)

        print 'Found', len(specialList)

        if len(specialList) is 0:
            return

        specialList.sort()
        qwd = QWD(configFile)

        for special in specialList:

            formatter = SpecialFormatter.create(special)

            print formatter.getPlate(qwd)
            runCommand('/usr/bin/eog {}'.format(formatter.getImage()))

            getchar()

    except:
        traceback.print_exc(file=sys.stdout)
    finally:
        db.quit()

if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf-8')

    num = len(sys.argv)
    if num < 2:
        print 'Usage:\n\t', sys.argv[0], 'key [lowPrice highPrice]'
        exit()

    configFile = 'config.ini'

    key = sys.argv[1]
    price = None

    if num is 4:
        price = (sys.argv[2], sys.argv[3])

    run(configFile, key, price)

