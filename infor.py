# -*- coding:utf-8 -*-

import json
import sys
import requests

from base import Comment
from utils import getMatchString

def getSlogan(skuid):

    SKU_MAIN_URL_TEMPLATE = 'http://item.m.jd.com/product/{}.html'
    url = SKU_MAIN_URL_TEMPLATE.format(skuid)

    r = requests.get(url)
    # TODO: add other judgement for http response

    #PATTERN = r'<div class="prod-act">(.*?)</div>'
    PATTERN = r'<div class="prod-act">(.*?)<'

    return getMatchString(r.text, PATTERN)

def getComment(skuid):

    COMMENT_URL_TEMPLATE = 'http://item.m.jd.com/ware/getDetailCommentList.json?wareId={}'
    url = COMMENT_URL_TEMPLATE.format(skuid)

    r = requests.get(url)
    # TODO: add other judgement for http response

    obj = json.loads(r.text)
    obj = obj.pop('wareDetailComment')

    return Comment(skuid, obj)

