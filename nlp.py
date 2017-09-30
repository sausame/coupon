#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import random
import requests
import sys

from utils import getProperty

class NLP:

    NLP_URL = ''
    NLP_API_KEYWORDS = ''

    NLP_ORIGIN = ''
    NLP_REFERER = ''
    NLP_USER_AGENT = ''

    @staticmethod
    def init(configFile):

        NLP.NLP_URL = getProperty(configFile, 'nlp-url')
        NLP.NLP_API_KEYWORDS = getProperty(configFile, 'nlp-api-keywords')

        NLP.NLP_ORIGIN = getProperty(configFile, 'nlp-origin')
        NLP.NLP_REFERER = getProperty(configFile, 'nlp-referer')
        NLP.NLP_USER_AGENT = getProperty(configFile, 'nlp-user-agent')

    @staticmethod
    def getKeywords(content):

        headers = {
            'Origin': NLP.NLP_ORIGIN,
            'Referer': NLP.NLP_REFERER,
            'User-Agent': NLP.NLP_USER_AGENT
        }

        cookies = {
            'pgv_pvi': '{}'.format(random.randint(1000000000, 9999999999)),
            'pgv_si': 's{}'.format(random.randint(1000000000, 9999999999))
        }

        data = {'api': 5, 'body_data': '{{"content":"{0}","title":"{0}"}}'.format(content)}

        r = requests.post(NLP.NLP_URL, cookies=cookies, data=data, headers=headers)

        if 200 != r.status_code:
            print 'Unable to get keywords for "', content, '" with an error (', r.status_code, '):\n', r.text
            return None

        obj = json.loads(r.content.decode('utf-8', 'ignore'))
        errCode = int(obj.pop('ret_code'))

        return obj.pop('keywords')

