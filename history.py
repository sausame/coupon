import json

from base import PromotionHistory, PriceHistoryData
from js import JsExecutor
from network import Network

class PriceHistory:

    def __init__(self):
        self.priceHistoryData = None

    def update(self, sku, executor):

        url = 'http://item.jd.com/{}.html'.format(sku.data['skuid']) # For history searching
        # Get URL for price history
        url = executor.context.requestPriceInfo(sku.data['title'], url)

        # Get price histories
        path = 'data/{}.js'.format(sku.data['skuid'])

        ret = Network.saveHttpData(path, url)
        print 'Update', path, ':', sku.data['title']

        if ret is 0:
            if self.parse(path) is not None:
                self.getPriceHistoryData()

    def parse(self, path):

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

        self.obj = json.loads(data)

        return self.obj

    def getPriceHistoryData(self):

        if self.priceHistoryData is not None:
            return self.priceHistoryData

        promotionHistoryList = None

        try:
            for data in self.obj['promotionHistory']:
                if promotionHistoryList is None:
                    promotionHistoryList = list()

                promotionHistoryList.append(PromotionHistory(data))
        except AttributeError:
            pass
        except KeyError:
            pass

        try:
            self.priceHistoryData = PriceHistoryData(self.obj['priceHistoryData'])
            self.priceHistoryData.updatePromotion(promotionHistoryList)
        except AttributeError:
            pass
        except KeyError:
            pass

        return self.priceHistoryData

class PriceHistoryManager:

    def __init__(self):
        self.priceHistoryDataList = None

    def getPriceHistoryDataList(self, skus=None, sku=None):

        executor = JsExecutor('js/huihui.js')

        if sku is not None:
            skus = [sku]

        self.priceHistoryDataList = list()

        for sku in skus:

            priceHistory = PriceHistory()
            priceHistory.update(sku, executor)
            priceHistoryData = priceHistory.getPriceHistoryData()

            self.priceHistoryDataList.append(priceHistoryData)

        return self.priceHistoryDataList

