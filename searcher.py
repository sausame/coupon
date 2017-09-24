#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import traceback

from db import Database
from evaluation import Evaluation
from utils import getchar

def run(configfile, key, price=None):

    try:

        db = Database(configFile, 'specials')
        db.initialize()

        evaluation = Evaluation(configFile, db)

        specialList = evaluation.search(key, price)

        print 'Found', len(specialList)

        for special in specialList:
            print special
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

