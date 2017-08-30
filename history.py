import json

from base import PromotionHistory, PriceHistoryData
from js import JsExecutor
from network import Network

class PriceHistoryManager:

    def __init__(self):
        self.priceHistoryDataList = None

    def getPriceHistoryDataList(self, skus=None, sku=None):

        executor = JsExecutor('js/huihui.js')

        if sku is not None:
            skus = [sku]

        self.priceHistoryDataList = list()

        for sku in skus:

            priceHistoryData = PriceHistoryManager.getPriceHistoryData(sku, executor)

            if priceHistoryData is not None:
                self.priceHistoryDataList.append(priceHistoryData)

        return self.priceHistoryDataList

    @staticmethod
    def getPriceHistoryData(sku, executor):

        url = 'http://item.jd.com/{}.html'.format(sku.data['skuid']) # For history searching
        # Get URL for price history
        url = executor.context.requestPriceInfo(sku.data['title'], url)

        # Get price histories
        path = 'data/{}.js'.format(sku.data['skuid'])

        ret = Network.saveHttpData(path, url)
        print 'Update', path, ':', sku.data['title']

        if ret is not 0:
            return None

        obj = PriceHistoryManager.parse(path)
        if obj is None:
            return None

        return PriceHistoryManager.generatePriceHistoryData(obj)

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
    def generatePriceHistoryData(obj):

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
        except AttributeError:
            pass
        except KeyError:
            pass

        return priceHistoryData

