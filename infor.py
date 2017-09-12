# -*- coding:utf-8 -*-

import json

from network import Network
from utils import getMatchString

def getSlogan(skuid):

    path = 'data/{}.html'.format(skuid)

    SKU_MAIN_URL_TEMPLATE = 'http://item.m.jd.com/product/{}.html'
    url = SKU_MAIN_URL_TEMPLATE.format(skuid)

    ret = Network.saveGetUrl(path, url)
    print 'Update', path, ':', ret

    if ret < 0:
        return None

    #PATTERN = r'<div class="prod-act">(.*?)</div>'
    PATTERN = r'<div class="prod-act">(.*?)<'

    with open(path) as fp:
        content = fp.read()

        slogan = getMatchString(content, PATTERN)
        if slogan is not None and not isinstance(slogan, unicode):
            slogan = unicode(slogan, errors='ignore')
        return slogan

    return None

def getComment(skuid):

    COMMENT_URL_TEMPLATE = 'http://item.m.jd.com/ware/getDetailCommentList.json?wareId={}'
    url = COMMENT_URL_TEMPLATE.format(skuid)

    path = 'data/{}.json'.format(skuid)

    ret = Network.saveGetUrl(path, url)
    print 'Update', path, ':', ret

    if ret < 0:
        return None

    with open(path) as fp:
        content = fp.read()
        obj = json.loads(content)
        return obj.pop('wareDetailComment')

    return None

