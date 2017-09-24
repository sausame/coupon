#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import traceback

from db import Database
from evaluation import Evaluation
from utils import getchar

def run(configfile, key):

    try:

        db = Database(configFile, 'specials')
        db.initialize()

        evaluation = Evaluation(configFile, db)

        specialList = evaluation.search(key)

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
        print 'Usage:\n\t', sys.argv[0], 'key [config-file]'
        exit()

    key = sys.argv[1]

    if num is 2:
        configFile = 'config.ini'
    elif num is 3:
        configFile = sys.argv[2]

    run(configFile, key)

