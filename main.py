#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys

from goods import SkuManager, CouponManager, DiscountManager, SeckillManager

if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf-8')

    couponManager = CouponManager('')
    discountManager = DiscountManager('')
    skuManager = SkuManager('')
    seckillManager = SeckillManager()

    couponManager.update()
    discountManager.update()
    seckillManager.update()

    skuList1 = skuManager.getSkuList(couponManager.skuIdList)
    skuList2 = skuManager.getSkuList(discountManager.skuIdList)
    skuList3 = skuManager.getSkuList(seckillManager.skuIdList)

    print '============================'
    #print len(skuList3), len(seckillManager.seckillList)
    print len(skuList1), len(skuList2), len(skuList3)

    '''
    ids = ['10155948944', '3256907']
    print skuManager.getSkuList(ids)
    '''

