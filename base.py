#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import math

from datetime import tzinfo, timedelta, datetime
from infor import getSlogan, getComments
from operator import attrgetter
from utils import seconds2Datetime, hexlifyUtf8, unhexlifyUtf8, UrlUtils

class BaseDict:

    def __init__(self, data):
        self.data = data

    def insert(self, db, tableName):
        keys = self.getAlterKeys()

        for key in keys:
            if key not in self.data.keys():
                self.data[key] = None

        db.insert(tableName, self.data, keys)

    def getAlterKeys(self):
        return None

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
        self.data['price'] = float(self.data.pop('price'))
        self.data['comRate'] = float(self.data.pop('comRate'))

        # TODO: Commission price can be calculate by price and comRate
        self.data['commissionprice'] = float(self.data.pop('commissionprice'))
        self.data['goodCom'] = int(self.data.pop('goodCom'))
        self.data['salecount'] = int(self.data.pop('salecount'))

    def getAlterKeys(self):
        return ['skuid', 'title']

class Coupon(SkuBase):

    def __init__(self, data):
        SkuBase.__init__(self, data)

        # Set as the same name
        self.data['skuid'] = int(self.data.pop('skuId'))

        # XXX: Sometimes quota is NOT as same as price in SKU, because the coupon
        # may be invalid then. So don't worry about that.
        self.data['quota'] = float(self.data.pop('quota'))
        self.data['denomination'] = float(self.data.pop('denomination'))
        self.data['usedNum'] = int(self.data.pop('usedNum'))
        self.data['couponNum'] = int(self.data.pop('couponNum'))
        self.data['specialPrice'] = self.data['quota'] - self.data['denomination']
        self.data['validBeginTime'] = int(self.data.pop('validBeginTime'))
        self.data['validEndTime'] = int(self.data.pop('validEndTime'))
        self.data['couponValid'] = int(self.data.pop('couponValid'))

    def getAlterKeys(self):
        return ['skuid', 'validBeginTime', 'validEndTime']

class Discount(SkuBase):

    def __init__(self, data):
        SkuBase.__init__(self, data)

        self.data['skuid'] = int(self.data.pop('skuid'))
        self.data['specialPrice'] = float(self.data.pop('promoPrice'))

    def getAlterKeys(self):
        return ['skuid']

class MatchesItem(BaseDict):

    def __init__(self, data):
        BaseDict.__init__(self, data)

class Seckill(BaseDict):

    def __init__(self, data):
        BaseDict.__init__(self, data)

        self.data['skuid'] = int(self.data.pop('wareId'))
        self.data['specialPrice'] = float(self.data.pop('miaoShaPrice'))

    def setPeriod(self, startTime, endTime):

        self.data['startTime'] = startTime
        self.data['endTime'] = endTime

    def getAlterKeys(self):
        return ['skuid', 'startTimeMills', 'rate', 'wname', 'tagText', 'cName', 'adword']

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

    def getAlterKeys(self):
        return ['skuid']

    def updatePromotion(self, promotionHistoryList):
        # TODO: Update history price by the promotion history
        pass

    def __repr__(self):
        fields = ['    {}={}'.format(k, v)
            for k, v in self.__dict__.items()
                if not k.startswith('_') and 'data' != k]

        str = BaseDict.__repr__(self)

        return '{}:\n{}\n{}'.format(self.__class__.__name__, '\n'.join(fields), str)

class SkuInformation(BaseDict):

    def __init__(self, data, version):
        BaseDict.__init__(self, data)

        self.data['skuid'] = int(self.data.pop('skuid'))
        self.data['version'] = version
        self.data['historyList'] = json.loads(self.data.pop('historyList'))

        keys = ['startTime', 'endTime']

        for key in keys:
            if key not in self.data.keys():
                self.data[key] = None

        if 'validBeginTime' in self.data.keys():
            self.data['startTime'] = seconds2Datetime(self.data.pop('validBeginTime') / 1000L)

        if 'validEndTime' in self.data.keys():
            self.data['endTime'] = seconds2Datetime(self.data.pop('validEndTime') / 1000L)

    def setSlogan(self, slogan):
        self.data['slogan'] = slogan

    def setComments(self, data):

        self.data.update(data)

        self.data.pop('code')

        self.data['allCnt'] = int(self.data.pop('allCnt'))
        self.data['goodCnt'] = int(self.data.pop('goodCnt'))
        self.data['badCnt'] = int(self.data.pop('badCnt'))
        self.data['normalCnt'] = int(self.data.pop('normalCnt'))
        self.data['pictureCnt'] = int(self.data.pop('pictureCnt'))
        self.data['showPicCnt'] = int(self.data.pop('showPicCnt'))
        self.data['consultationCount'] = int(self.data.pop('consultationCount'))
        self.data['percentOfGoodComments'] = self.data.pop('goods')

        commentInfoList = list()
        for info in self.data.pop('commentInfoList'):

            commentInfo = dict()

            commentInfo['commentShareUrl'] = info['commentShareUrl']
            commentInfo['userNickName'] = info['userNickName']
            commentInfo['commentData'] = hexlifyUtf8(info['commentData'])
            commentInfo['commentScore'] = int(info['commentScore'])

            commentInfoList.append(commentInfo)

        self.data['commentList'] = json.dumps(commentInfoList, ensure_ascii=False,
                indent=4, sort_keys=True)

    def getAlterKeys(self):
        return ['skuid', 'slogan', 'commentList']

    def updatePrices(self):

        nowPrice = self.data['specialPrice']

        self.prices = list()
        self.histories = list()

        self.histories.append(PriceHistory(price=float(nowPrice), time=datetime.now().strftime('%Y-%m-%d')))

        for history in self.data.pop('historyList'):
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

    def updateSlogan(self):

        slogan = getSlogan(self.data['skuid'])

        if slogan is not None:
            self.setSlogan(slogan)

    def updateComments(self):

        comments = getComments(self.data['skuid'])

        if comments is not None:
            self.setComments(comments)

    def updateCouponLink(self):

        couponLink = None
        if 'couponLink' in self.data.keys():
            url = self.data.pop('couponLink')
            if url is not None:
                pos = url.find('?')
                if pos > 0:
                    url = 'http://coupon.m.jd.com/coupons/show.action{}'.format(url[pos:])
                    couponLink = UrlUtils.toShortUrl(url)

        self.data['couponLink'] = couponLink

    def update(self):

        self.updatePrices()
        self.updateSlogan()
        self.updateComments()
        self.updateCouponLink()

class Special(SkuBase):

    def __init__(self, data):
        SkuBase.__init__(self, data)

        self.data['commentList'] = json.loads(self.data.pop('commentList'))

        for i in range(len(self.data['commentList'])):
            self.data['commentList'][i]['commentData'] = unhexlifyUtf8(self.data['commentList'][i].pop('commentData'))

    def updateDb(self, db, tableName):

        data = dict()

        data['id'] = self.data['id']
        data['used'] = True

        db.update(tableName, data, ['id'])

    def updateOutput(self, qwd):

        self.title = self.data['title']
        self.slogan = self.data['slogan']

        self.price = self.data['price']
        self.avgPrice = self.data['avgPrice']
        self.specialPrice = self.data['specialPrice']
        self.totalDays = self.data['totalDays']

        self.percentOfGoodComments = self.data['percentOfGoodComments']

        if self.data['startTime'] is not None and self.data['endTime'] is not None:
            self.period = u'时间：{}到{}'.format(self.data['startTime'],
                    self.data['endTime'])
        else:
            self.period = ''

        self.comments = ''
        for comment in self.data['commentList']:

            if '' == self.comments:
                self.comments = u'用户评价：\n'

            self.comments += u'{}：{}\n'.format(comment['userNickName'], comment['commentData'])

        if self.data['couponLink'] is not None:
            self.couponLink = u'领券：{}'.format(self.data['couponLink'])
        else:
            self.couponLink = ''

        self.shareUrl = qwd.getShareUrl(self.data['skuid'])

    def update(self, qwd, db, tableName):

        self.updateDb(db, tableName)
        self.updateOutput(qwd)

    def __repr__(self):
        with open('plate/special.txt') as fp:
            content = fp.read().format(self)

        return content

