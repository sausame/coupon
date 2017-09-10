#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import os

from base import MatchesItem, Seckill
from network import Network

class SeckillInfo:

    def __init__(self, gid, db):

        self.seckillInfo = None

        self.matchesList = None
        self.skuIdList = None
        self.seckillList = None

        self.gid = gid

        self.db = db

    def update(self):

        path = 'data/%d.json' % self.gid

        ret = Network.saveHttpData(path, 'http://coupon.m.jd.com/seckill/seckillList.json?gid=%d' % self.gid)
        if ret < 0:
            return False

        print 'Retrieve', path

        return self.parse(path)

    def parse(self, path):

        def getJsonString(path):

            with open(path) as fh:
                return 0, fh.read()

            return -1, ""

        ret, data = getJsonString(path)

        if ret < 0:
            print 'Wrong format: {}'.format(path)
            return False

        obj = json.loads(data)
        self.seckillInfo = obj.pop('seckillInfo')

        return True

    def getMatchesList(self):

        if self.matchesList is not None:
            return self.matchesList

        self.matchesList = list()

        for data in self.seckillInfo['matchesList']:
            self.matchesList.append(MatchesItem(data))

        return self.matchesList

    def getSkuIdList(self):

        if self.skuIdList is not None:
            return self.self.skuIdList

        self.skuIdList = list()

        for data in self.seckillInfo['itemList']:
            self.skuIdList.append(data['wareId'])

        return self.skuIdList

    def getSeckillList(self):

        if self.seckillList is not None:
            return self.seckillList

        self.getMatchesList()

        # Find current matchesItem
        for matchesItem in self.matchesList:

            if matchesItem.data['gid'] == self.gid:
                startTime = matchesItem.data['startTime']
                endTime = matchesItem.data['endTime']

                break;

        else:
            return None

        self.seckillList = list()

        for data in self.seckillInfo['itemList']:

            if self.db.findOne('SeckillTable', skuid=data['wareId']):
                # Already exists
                continue

            seckill = Seckill(data)
            seckill.setPeriod(startTime, endTime)

            self.db.insert('SeckillTable', seckill.data, ['skuid',
                'startTimeMills', 'rate', 'wname', 'tagText', 'cName',
                'tips', 'mTips', 'adword'])

            self.seckillList.append(seckill)

        return self.seckillList

class SeckillManager:

    def __init__(self, db, isLocal=False):

        self.db = db

        self.isLocal = isLocal

        self.skuIdList = None

        self.seckillInfoList = None
        self.seckillList = None

        try:
            os.mkdir('data')
        except OSError:
            pass

    def getGidList(self):

        ENTRANCE_GID = 26

        seckillInfo = SeckillInfo(ENTRANCE_GID, self.db)

        if not seckillInfo.update():
            return None

        matchesList = seckillInfo.getMatchesList()

        gids = list()

        for matchesItem in matchesList:
            gids.append(matchesItem.data['gid'])

        return gids

    def updateSeckillInfoList(self):

        self.seckillInfoList = list()

        gids = self.getGidList()

        for gid in gids:

            seckillInfo = SeckillInfo(gid, self.db)

            if not seckillInfo.update():
                continue

            self.seckillInfoList.append(seckillInfo)

    def updateSkuIdList(self):

        self.skuIdList = list()

        for seckillInfo in self.seckillInfoList:

            self.skuIdList.extend(seckillInfo.getSkuIdList())

    def updateSeckillList(self):

        self.seckillList = list()

        for seckillInfo in self.seckillInfoList:

            self.seckillList.extend(seckillInfo.getSeckillList())

    def update(self):

        self.updateSeckillInfoList()
        self.updateSkuIdList()
        self.updateSeckillList()

