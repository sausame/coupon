#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import math

from datetime import tzinfo, timedelta, datetime
from functools import total_ordering
from imgkit import ImageKit
from infor import getSlogan, getComments
from operator import attrgetter
from utils import seconds2Datetime, hexlifyUtf8, unhexlifyUtf8, UrlUtils
from validation import Validation

class BaseDict:

    def __init__(self, data):
        self.data = data

    def insert(self, db, tableName):

        if db is None or tableName is None:
            return

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
        self.data['cutPrice'] = self.data['quota'] - self.data['denomination']
        self.data['validBeginTime'] = int(self.data.pop('validBeginTime'))
        self.data['validEndTime'] = int(self.data.pop('validEndTime'))
        self.data['couponValid'] = int(self.data.pop('couponValid'))

    def getAlterKeys(self):
        return ['skuid', 'validBeginTime', 'validEndTime']

class Discount(SkuBase):

    def __init__(self, data):
        SkuBase.__init__(self, data)

        self.data['skuid'] = int(self.data.pop('skuid'))
        self.data['cutPrice'] = float(self.data.pop('promoPrice'))

    def getAlterKeys(self):
        return ['skuid']

class MatchesItem(BaseDict):

    def __init__(self, data):
        BaseDict.__init__(self, data)

class Seckill(BaseDict):

    def __init__(self, data):
        BaseDict.__init__(self, data)

        self.data['skuid'] = int(self.data.pop('wareId'))
        self.data['title'] = self.data.pop('wname')
        self.data['cutPrice'] = float(self.data.pop('miaoShaPrice'))
        self.data['jdPrice'] = float(self.data.pop('jdPrice'))

    def setPeriod(self, startTime, endTime):

        self.data['startTime'] = startTime
        self.data['endTime'] = endTime

    def getAlterKeys(self):
        return ['skuid', 'startTimeMills', 'rate', 'title', 'tagText', 'cName', 'adword', 'mTips', 'tips']

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

        self.data['skuid'] = int(self.data.pop('skuid'))

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

        if 'outputTime' not in self.data.keys():
            if self.data['startTime'] is None:
                self.data['outputTime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            else:
                self.data['outputTime'] = self.data['startTime']

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

        cutPrice = self.data['cutPrice']

        # Correct cut-price if not right
        if cutPrice > self.data['price']:
            self.priceCorrected = True
            cutPrice = self.data['price']
        else:
            self.priceCorrected = False

        self.prices = list()
        self.histories = list()

        self.histories.append(PriceHistory(price=float(cutPrice), time=datetime.now().strftime('%Y-%m-%d')))

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
        discount = int(100 * float(cutPrice) / float(avgPrice))
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
        lowestDiscount = float(cutPrice) / float(lowestPrice)

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

@total_ordering
class Special(SkuBase):

    def __init__(self, data):
        SkuBase.__init__(self, data)

        self.data['commentList'] = json.loads(self.data.pop('commentList'))

        for i in range(len(self.data['commentList'])):
            self.data['commentList'][i]['commentData'] = unhexlifyUtf8(self.data['commentList'][i].pop('commentData'))

    def update(self, db=None, tableName=None):

        if db is None or tableName is None:
            return

        if 'outputTime' not in self.data.keys():
            return

        data = dict()

        data['id'] = self.data['id']

        # XXX: Postpone and set outputTime to that after next three days
        data['outputTime'] = (datetime.now() + timedelta(days=3)).replace(minute=0,
                second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S')

        db.update(tableName, data, ['id'])

    def __lt__(self, other):
        return (self.data['weight'] < other.data['weight'])

    def __gt__(self, other):
        return (self.data['weight'] > other.data['weight'])

class SpecialFormatter:

    def __init__(self, special):
        self.special = special

    def prepare(self):

        self.skuid = self.special.data['skuid']
        self.title = self.special.data['title']
        self.slogan = self.special.data['slogan']

        if self.slogan is None:
            self.slogan = ''

        self.skuimgurl = self.special.data['skuimgurl']

        self.price = self.special.data['price']
        self.lowestPrice = self.special.data['lowestPrice']
        self.avgPrice = self.special.data['avgPrice']
        self.cutPrice = self.special.data['cutPrice']

        self.totalDays = self.special.data['totalDays']
        self.percentOfGoodComments = self.special.data['percentOfGoodComments']

        self.startTime = self.special.data['startTime']
        self.endTime = self.special.data['endTime']

        self.comments = list()

        for comment in self.special.data['commentList']:

            if Validation.isCommentBad(comment['commentData']):
                continue

            self.comments.append(comment)

        self.couponLink = self.special.data['couponLink']

    def preparePlate(self, qwd):

        if self.avgPrice < self.price:
            self.plateAvgPrice = '均　　价：￥{}'.format(self.avgPrice)
        else:
            self.plateAvgPrice = ''

        if self.totalDays < 30:
            self.plateTotalDays = '{}天'.format(self.totalDays)
        elif self.totalDays < 360:
            self.plateTotalDays = '{}个月'.format(self.totalDays/30)
        else:
            self.plateTotalDays = '超过1年'

        if self.startTime is not None and self.endTime is not None:
            self.platePeriod = u'特价时间：{}到{}'.format(self.startTime, self.endTime)
        else:
            self.platePeriod = ''

        self.plateComments = ''

        for comment in self.comments:
            commentData = comment['commentData'].replace('\n', '')

            self.plateComments += u'{}：{}\n'.format(comment['userNickName'], commentData)

        if self.couponLink is not None:
            self.plateCouponLink = u'领券：{}'.format(self.couponLink)
        else:
            self.plateCouponLink = ''

        self.plateShareUrl = qwd.getShareUrl(self.skuid)

    def getPlate(self, qwd):

        self.preparePlate(qwd)

        with open('plate/special.txt') as fp:
            content = fp.read().format(self)

        return content.replace('\n\n', '\n')

    def prepareHtml(self):

        self.discount = int(self.cutPrice * 100 / self.price)
        self.lowestRatio = int(self.lowestPrice * 100 / self.price)
        self.avgRatio = int(self.avgPrice * 100 / self.price)
        self.curRatio = 100

        maxRatio = 80

        self.discountDisplay = int(self.cutPrice * maxRatio / self.price)
        self.lowestRatioDisplay = int(self.lowestPrice * maxRatio / self.price)
        self.avgRatioDisplay = int(self.avgPrice * maxRatio / self.price)
        self.curRatioDisplay = maxRatio

        # Colors
        if self.totalDays < 30:
            self.totalDaysColor = 'rgb(255, 57, 31)'
        elif self.totalDays < 60:
            self.totalDaysColor = 'rgb(255, 169, 33)'
        elif self.totalDays < 90:
            self.totalDaysColor = 'rgb(5, 157, 127)'
        else:
            self.totalDaysColor = '#666'

    def getHtml(self):

        self.prepareHtml()

        with open('html/special.html') as fp:
            content = fp.read().format(self)

        return content

    def getImage(self):

        content = self.getHtml()

        path = '{}.html'.format(self.skuid)

        with open(path, 'w') as fp:
            fp.write(content)

        return ImageKit.fromHtml(path)

