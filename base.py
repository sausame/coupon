#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import math

from datetime import tzinfo, timedelta, datetime
from operator import attrgetter

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

        self.data['skuid'] = int(self.data.pop('skuid'))

class Coupon(SkuBase):

    def __init__(self, data):
        SkuBase.__init__(self, data)

        # Set as the same name
        self.data['skuid'] = int(self.data.pop('skuId'))

class Discount(SkuBase):

    def __init__(self, data):
        SkuBase.__init__(self, data)

        self.data['skuid'] = int(self.data.pop('skuid'))

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

class PriceHistory:

    def __init__(self, **kwargs):
        self.set(**kwargs)

    def set(self, **kwargs):
        for keyword in ['price', 'time']:
            setattr(self, keyword, kwargs[keyword])

    def __repr__(self):
        fields = ['    {}={!r}'.format(k, v)
            for k, v in self.__dict__.items() if not k.startswith('_')]

        return '  {}:\n{}'.format(self.__class__.__name__, '\n'.join(fields))

class Price:

    def __init__(self, price, days, ratio):
        self.price = price
        self.days = days
        self.ratio = ratio

    def __repr__(self):
        fields = ['    {}={!r}'.format(k, v)
            for k, v in self.__dict__.items() if not k.startswith('_')]

        return '  {}:\n{}'.format(self.__class__.__name__, '\n'.join(fields))

class PriceHistoryData(BaseDict):

    def __init__(self, data):
        BaseDict.__init__(self, data)

    def updatePromotion(self, promotionHistoryList):
        # TODO: Update history price by the promotion history
        pass

    def update(self, sku):

        nowPrice = sku.data['price']

        self.prices = list()
        self.histories = list()

        self.histories.append(PriceHistory(price=float(nowPrice), time=datetime.now().strftime('%Y-%m-%d')))

        for history in self.data['list']:
            self.histories.append(PriceHistory(price=float(history['price']), time=history['time']))

        # Sort histories
        self.histories.sort(key=attrgetter('time'))

        # Calculate prices ratios
        prices = []
        totalDays = 0

        size = len(self.histories)

        for i in range(0, size):

            history = self.histories[i]
            days = 1

            if i < size - 1:
                thisDate = datetime.strptime(history.time, '%Y-%m-%d')
                nextDate = datetime.strptime(self.histories[i+1].time, '%Y-%m-%d')

                days = (nextDate - thisDate).days

            totalDays += days

            prices.append((history.price, days))

        prices.sort()

        pos = -1
        for price in prices:
            if pos >= 0 and self.prices[pos].price == price[0]:
                self.prices[pos].days += price[1]
                self.prices[pos].ratio = float(self.prices[pos].days) / float(totalDays)
            else:
                self.prices.append(Price(price[0], price[1], float(price[1]) / float(totalDays)))
                pos += 1

        # Calculate prices and discounts
        lowestPrice = float(int(100 * self.prices[0].price)) / 100

        avgPrice = 0.0
        for price in self.prices:
            avgPrice += float(price.price) * price.ratio

        avgPrice = float(int(100 * avgPrice)) / 100

        # Calculate discounts
        discount = int(100 * float(nowPrice) / float(avgPrice))
        if 0 == discount:
            discount = 1

        lowestRatio = int(100 * float(lowestPrice) / float(avgPrice))

        # Calculate weights
        '''
        Weight should be measured by factors as following:
        1, discount relative to lowest prices
        2, discount relative to average prices
        3, off amount
        4, days
        '''
        lowestDiscount = float(nowPrice) / float(lowestPrice)

        lg = math.log(totalDays)
        if 0 == lg: lg = 0.1 # Log(1) is 0.0

        weight = lowestDiscount / lg

        self.data['totalDays'] = totalDays
        self.data['weight'] = weight
        self.data['lowestPrice'] = lowestPrice
        self.data['avgPrice'] = avgPrice
        self.data['discount'] = discount
        self.data['lowestRatio'] = lowestRatio

    def __repr__(self):
        fields = ['    {}={}'.format(k, v)
            for k, v in self.__dict__.items()
                if not k.startswith('_') and 'data' != k]

        str = BaseDict.__repr__(self)

        return '{}:\n{}\n{}'.format(self.__class__.__name__, '\n'.join(fields), str)

