#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json

class BaseDict:

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return json.dumps(self.data, ensure_ascii=False, indent=4, sort_keys=True)

class SkuBase(BaseDict):

    def __init__(self, data):
        BaseDict.__init__(self, data)

    def equals(self, skuid):
        return skuid == self.data['skuid']

class Sku(SkuBase):

    def __init__(self, data):
        SkuBase.__init__(self, data)

class Coupon(SkuBase):

    def __init__(self, data):
        SkuBase.__init__(self, data)

        # Set as the same name
        self.data['skuid'] = self.data.pop('skuId')

class Discount(SkuBase):

    def __init__(self, data):
        SkuBase.__init__(self, data)

class MatchesItem(BaseDict):

    def __init__(self, data):
        BaseDict.__init__(self, data)

class Seckill(BaseDict):

    def __init__(self, data):
        BaseDict.__init__(self, data)

    def setPeriod(self, startTime, endTime):

        self.data['startTime'] = startTime
        self.data['endTime'] = endTime

class PromotionHistory(BaseDict):

    def __init__(self, data):
        BaseDict.__init__(self, data)

class PriceHistoryData(BaseDict):

    def __init__(self, data):
        BaseDict.__init__(self, data)

    def updatePromotion(self, promotionHistoryList):
        # TODO: Update history price by the promotion history
        pass

