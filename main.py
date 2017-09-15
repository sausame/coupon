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

        skuIds = list()

        skuIds.extend(couponManager.skuIdList)
        skuIds.extend(discountManager.skuIdList)
        skuIds.extend(seckillManager.skuIdList)

        skuManager.update(skuIds)

        evaluation.update()

        skuList1 = skuManager.retrieveSkuList(couponManager.newSkuIdList)[0]
        skuList2 = skuManager.retrieveSkuList(discountManager.newSkuIdList)[0]
        skuList3 = skuManager.retrieveSkuList(seckillManager.newSkuIdList)[0]

        print '============================'
        print len(skuList1), len(skuList2), len(skuList3)

        skus = list()
        skus.extend(skuList1)
        skus.extend(skuList2)
        skus.extend(skuList3)

        print '============================'
        print len(skus)

        '''
        ids = ['10155948944', '3256907']
        skus = skuManager.retrieveSkuList(ids)
        '''

        priceHistoryDataList = priceHistoryManager.getPriceHistoryDataList(skus=skus)
        print '============================'
        print len(priceHistoryDataList)

        #print priceHistoryDataList

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

