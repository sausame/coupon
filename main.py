#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import traceback

from coupon import SkuManager, CouponManager, DiscountManager
from db import Database
from evaluation import Evaluation
from seckill import SeckillManager
from history import PriceHistoryManager

def run(configfile):

    try:

        db = Database(configFile, 'specials')
        db.initialize()

        skuManager = SkuManager(configFile, db)

        couponManager = CouponManager(configFile, db)
        discountManager = DiscountManager(configFile, db)
        seckillManager = SeckillManager(db)

        priceHistoryManager = PriceHistoryManager(db)
        evaluation = Evaluation(configFile, db)

        couponManager.update()
        discountManager.update()
        seckillManager.update()

        skuManager.update()
        evaluation.update()

        priceHistoryManager.update()

        evaluation.evaluate()

    except:
        traceback.print_exc(file=sys.stdout)
    finally:
        db.quit()

if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf-8')

    configFile = 'config.ini'

    run(configFile)

