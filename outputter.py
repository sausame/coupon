#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import traceback

from base import SpecialFormatter
from db import Database
from evaluation import Evaluation
from qwd import QWD
from utils import getchar, getProperty, reprDict, runCommand, OutputPath

def run(configfile):

    OutputPath.init(configFile)

    try:

        db = Database(configFile, 'specials')
        db.initialize()

        evaluation = Evaluation(configFile, db)

        qwd = QWD(configFile)

        path = getProperty(configFile, 'output-share-file')

        data = evaluation.output()

        with open(path, 'w') as fp:
            fp.write(reprDict(data))

    except:
        traceback.print_exc(file=sys.stdout)
    finally:
        db.quit()

if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf-8')

    configFile = 'config.ini'

    run(configFile)

