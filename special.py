#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import requests

from base import SpecialFormatter
from datetime import datetime
from imgkit import ImageKit
from network import Network
from utils import getProperty, randomSleep, OutputPath

class Searcher:

    def __init__(self, configFile, qwd):

        self.qwd = qwd

        self.url = getProperty(configFile, 'search-url')
        self.configFile = configFile

    def search(self, content):

        r = Network.post(self.url, data={'content': content})

        if r is None:
            print 'No result for', content
            return False

        try:
            obj = json.loads(r.content.decode('utf-8', 'ignore'))
        except ValueError as e:
            print 'Error (', e, ') of json: "', r.content, '"'
            return False

        num = obj['num']
        if num is 0:
            print 'Error content: "', r.content, '"'
            return False

        print 'Found', num, 'SKU with "', content, '"'

        datas = obj['list']

        plates = list()
        urls = list()

        for data in datas:

            formatter = SpecialFormatter.create(data)

            plate = formatter.getPlate(self.qwd)
            url = data['skuimgurl']

            plates.append(plate)
            urls.append(url)

        now = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        path = OutputPath.getDataPath('search_{}'.format(now), 'jpeg')

        self.plate = '\n----------------------------\n'.join(plates)
        self.image = ImageKit.concatUrlsTo(path, urls)

        return True

class Viewer:

    def __init__(self, configFile, qwd):

        self.qwd = qwd

        self.url = getProperty(configFile, 'share-url')
        self.imageType = int(getProperty(configFile, 'share-image-type'))

    def get(self):

        r = requests.get(self.url)
        obj = json.loads(r.content)

        print 'Updated', obj['num'], 'SKU between', obj['startTime'], 'and', obj['endTime']

        if obj['num'] is 0:
            return obj

        dataList = list()

        for special in obj.pop('list'):

            data = dict()

            formatter = SpecialFormatter.create(special)

            data['plate'] = formatter.getPlate(self.qwd)
            data['image'] = formatter.skuimgurl

            dataList.append(data)

            randomSleep(1, 2)

        obj['list'] = dataList

        return obj

