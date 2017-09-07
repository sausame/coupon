import json

from base import PromotionHistory, PriceHistoryData
from js import JsExecutor
from network import Network

class PriceHistoryManager:

    def __init__(self, db):
        self.priceHistoryDataList = None
        self.db = db

    def getPriceHistoryDataList(self, skus=None, sku=None):

        executor = JsExecutor('js/huihui.js')

        if sku is not None:
            skus = [sku]

        self.priceHistoryDataList = list()

        for sku in skus:
            self.create(executor, sku)

        return self.priceHistoryDataList

    def create(self, executor, sku):

        skuid = sku.data['skuid']

        if self.db.findOne('HistoryTable', skuid=skuid):
            # Already exists
            return None

        title = sku.data['title']

        priceHistoryData = PriceHistoryManager.getPriceHistoryData(executor, sku)

        if priceHistoryData is None:
            return None

        self.db.insert('HistoryTable', priceHistoryData.data, ['skuid'])

        self.priceHistoryDataList.append(priceHistoryData)

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
        print 'Update', path, ':', title

        if ret is not 0:
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
            priceHistoryData.update(sku)

            priceHistoryData.data['list'] = json.dumps(priceHistoryData.data.pop('list'),
                    ensure_ascii=False, indent=4, sort_keys=True)

        except AttributeError:
            pass
        except KeyError:
            pass

        return priceHistoryData



