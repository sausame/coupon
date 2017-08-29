#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import traceback

from coupon import SkuManager, CouponManager, DiscountManager
from db import Database
from seckill import SeckillManager
from history import PriceHistoryManager

def run(configfile):

    try:

        db = Database(configFile, 'specials')
        db.initialize()

        skuManager = SkuManager(configFile, db)

        couponManager = CouponManager(configFile, db)
        discountManager = DiscountManager(configFile, db)
        seckillManager = SeckillManager()

        priceHistoryManager = PriceHistoryManager()

        couponManager.update()
        discountManager.update()
        seckillManager.update()

        skuList1 = skuManager.getSkuList(couponManager.skuIdList)
        skuList2 = skuManager.getSkuList(discountManager.skuIdList)
        skuList3 = skuManager.getSkuList(seckillManager.skuIdList)

        print '============================'
        #print len(skuList3), len(seckillManager.seckillList)
        print len(skuList1), len(skuList2), len(skuList3)

        skus = list()
        skus.extend(skuList1)
        skus.extend(skuList2)
        skus.extend(skuList3)

        print '============================'
        print len(skus)

        '''
        ids = ['10155948944', '3256907']
        skus = skuManager.getSkuList(ids)
        '''

        priceHistoryDataList = priceHistoryManager.getPriceHistoryDataList(skus=skus)
        print '============================'
        print len(priceHistoryDataList)

        print priceHistoryDataList

    except:
        traceback.print_exc(file=sys.stdout)
    finally:
        db.quit()

if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf-8')

    configFile = 'config.ini'

    run(configFile)

