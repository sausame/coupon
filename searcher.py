#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import traceback

from base import SpecialFormatter
from db import Database
from evaluation import Evaluation
from qwd import QWD
from utils import getchar, runCommand

def run(configfile, content):

    try:

        db = Database(configFile, 'specials')
        db.initialize()

        evaluation = Evaluation(configFile, db)

        specialList = evaluation.search(content)

        if specialList is None or len(specialList) is 0:
            return

        print 'Found', len(specialList)

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
        print 'Usage:\n\t', sys.argv[0], 'content'
        print '\tOr'
        print '\t', sys.argv[0], '\"#key#[low-price#[high-price#]]\"'
        exit()

    configFile = 'config.ini'
    content = sys.argv[1]

    run(configFile, content)

