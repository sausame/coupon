#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys

from goods import SkuManager, CouponManager, DiscountManager

if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf-8')

    couponManager = CouponManager('')
    discountManager = DiscountManager('')
    skuManager = SkuManager('')

    couponManager.update()
    discountManager.update()

    skuList1 = skuManager.getSkuList(couponManager.skuIdList)
    skuList2 = skuManager.getSkuList(discountManager.skuIdList)

    print '============================'
    print len(skuList1), len(skuList2)

