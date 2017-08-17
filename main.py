#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2017/7/26 15:48
# @Author  : lingxiangxiang
# @File    : main.py
import sys

from goods import Sku, SkuManager

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')

    apptoken = '79E42B6A507B803B76E4C3104B9AF9ED9F810155F84F62F034501870222BF014CC0B40847660A3DF142683DE1A578BFDB571112D1845A28449F5C15391B222E6'

    skus = SkuManager(apptoken=apptoken)
    print(skus.SkuidsDict)
    print(skus.other_all_skuids)
    print(len(skus.SkuidsDict))
    print(len(skus.other_all_skuids))
    # for i in skus.other_all_skuids:
    #     print(len(i))


