#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys

from coupon import SkuManager, CouponManager, DiscountManager
from seckill import SeckillManager
from history import PriceHistoryManager

if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf-8')

    skuManager = SkuManager('')

    couponManager = CouponManager('')
    discountManager = DiscountManager('')
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

