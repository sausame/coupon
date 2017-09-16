#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import traceback

from db import Database
from evaluation import Evaluation

def run(configfile):

    try:

        db = Database(configFile, 'specials')
        db.initialize()

        evaluation = Evaluation(configFile, db)
        evaluation.output()

    except:
        traceback.print_exc(file=sys.stdout)
    finally:
        db.quit()

if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf-8')

    configFile = 'config.ini'

    run(configFile)

