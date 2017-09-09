#!/usr/bin/env python
# -*- coding:utf-8 -*-

from base import Special

class Evaluation:

    VERSION = 1.0

    def __init__(self, configFile, db):

        self.configFile = configFile
        self.db = db

    def evaluate(self, manager, priceHistoryManager):

        if isinstance(manager, CouponManager):
            pass
        elif isinstance(manager, DiscountManager):
            pass
        elif isinstance(manager, SeckillManager):
            pass

    def store(self):
        pass

