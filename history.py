import json

from base import Sku, PromotionHistory, PriceHistoryData
from js import JsExecutor
from network import Network

class PriceHistoryManager:

    def __init__(self, db=None):
        self.priceHistoryDataList = None
        self.db = db

        self.executor = JsExecutor('js/huihui.js')

    def update(self):

        sql = 'SELECT id FROM HistoryTable LIMIT 1'
        result = self.db.query(sql)

        sql = 'SELECT * FROM SkuTable'
        where = ' WHERE skuid NOT IN (SELECT skuid FROM HistoryTable) '

        if result is not None:
            sql += where

        result = self.db.query(sql)

        if result is None:
            return

        self.priceHistoryDataList = list()

        for row in result:

            priceHistoryData = self.create(Sku(row))
            self.priceHistoryDataList.append(priceHistoryData)

    def create(self, sku):

        skuid = sku.data['skuid']

        if self.db is not None and self.db.findOne('HistoryTable', skuid=skuid):
            # Already exists
            return None

        title = sku.data['title']

        priceHistoryData = PriceHistoryManager.getPriceHistoryData(self.executor, sku)

        if priceHistoryData is None:
            return None

        priceHistoryData.insert(self.db, 'HistoryTable')

        return priceHistoryData

    @staticmethod
    def getPriceHistoryData(executor, sku):

        skuid = sku.data['skuid']
        title = sku.data['title']

        url = 'http://item.jd.com/{}.html'.format(skuid) # For history searching
        # Get URL for price history
        url = executor.context.requestPriceInfo(title, url)

        # Get price histories
        path = 'data/{}.js'.format(skuid)

        ret = Network.saveHttpData(path, url)
        #print 'Update', path, ':', ret, ':', title

        if ret < 0:
            return None

        obj = PriceHistoryManager.parse(path)
        if obj is None:
            return None

        return PriceHistoryManager.generatePriceHistoryData(sku, obj)

    @staticmethod
    def parse(path):

        def getJsonString(path):

            try:
                with open(path) as fh:
                    for line in fh.readlines(): 
                        if len(line) > 1024:

                            start = line.find('{')
                            end = line.rfind('}')

                            return line[start:end+1]
            except IOError:
                pass

            return None

        data = getJsonString(path)

        if not data:
            print 'Wrong format: {}'.format(path)
            return None

        return json.loads(data)

    @staticmethod
    def generatePriceHistoryData(sku, obj):

        priceHistoryData = None
        promotionHistoryList = None

        try:
            for data in obj['promotionHistory']:
                if promotionHistoryList is None:
                    promotionHistoryList = list()

                promotionHistoryList.append(PromotionHistory(data))
        except AttributeError:
            pass
        except KeyError:
            pass

        try:
            priceHistoryData = PriceHistoryData(obj['priceHistoryData'])
            priceHistoryData.updatePromotion(promotionHistoryList)

            priceHistoryData.data['skuid'] = sku.data['skuid']
            priceHistoryData.data['list'] = json.dumps(priceHistoryData.data.pop('list'),
                    ensure_ascii=False, indent=4, sort_keys=True)

        except AttributeError as e:
            pass
        except KeyError as e:
            pass

        return priceHistoryData

