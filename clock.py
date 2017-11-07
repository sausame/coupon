#!/usr/bin/env python
# -*- coding:utf-8 -*-

import random
import sys
import math

from datetime import timedelta, datetime
from utils import reprDict

class Clock:

    def __init__(self, days=3, hourRange=(7, 21, 2)):

        today = datetime.now().replace(hour=0, minute=0,
                second=0, microsecond=0)

        self.times = list()

        for i in range(days):

            for hour in range(*hourRange):

                data = dict()

                data['time'] = today.replace(hour=hour).strftime('%Y-%m-%d %H:%M:%S')
                data['count'] = 0

                self.times.append(data)

            today += timedelta(days=1)

        self.size = len(self.times)
        self.count = 0

    def randomTime(self, tillTime=None):

        self.count += 1

        actualSize = self.size
        avgCount = math.ceil(float(self.count) / self.size)

        if tillTime is not None:

            if tillTime <= self.times[0]['time']:
                return tillTime

            tillTime = datetime.strptime(tillTime, '%Y-%m-%d %H:%M:%S').replace(minute=0,
                    second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S')

            if tillTime < self.times[self.size - 1]['time']:

                minCount = sys.maxint
                maxCount = 0

                actualSize = 0

                for data in self.times:

                    if data['time'] >= tillTime:
                        break

                    count = data['count']

                    if count < minCount:
                        minCount = count

                    if count > maxCount:
                        maxCount = count

                    actualSize += 1

                if actualSize is 0:
                    return tillTime # Invalid

                if minCount == maxCount:
                    avgCount = maxCount + 1
                else: # max > min
                    avgCount = maxCount

        num = random.randint(0, actualSize)

        ranges = [(num, actualSize), (0, num)]

        for aRange in ranges:

            for i in range(*aRange):

                if self.times[i]['count'] < avgCount:

                    self.times[i]['count'] += 1
                    return self.times[i]['time']

        # XXX: Should not be here
        raise Exception('Error: random {}, till {}'.format(num, tillTime))

    def __repr__(self):
        return reprDict(self.times)

