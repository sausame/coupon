# -*- coding:utf-8 -*-

import json
import re

from network import Network
from utils import getMatchString, OutputPath

class Infor:

    SKU_MAIN_URL_TEMPLATE = 'http://item.m.jd.com/product/{}.html'
    COMMENT_URL_TEMPLATE = 'http://item.m.jd.com/ware/getDetailCommentList.json?wareId={}'

    SLOGAN_PATTERN = r'<div class="prod-act[-\s\w]*">(.*?)<'
    IMAGE_PATTERN = r'<img\s+src="https://m.360buyimg.com/n12/jfs[./!\w]+"'
    MARK_PATTERN = r'"(.*?)"'

    def __init__(self, skuid):
        self.skuid = skuid

    def getImage(self):

        path = OutputPath.getDataPath(self.skuid, 'html')
        url = Infor.SKU_MAIN_URL_TEMPLATE.format(self.skuid)

        ret = Network.saveGetUrl(path, url)

        if ret < 0:
            return None

        with open(path) as fp:
            content = fp.read()

            m = re.search(Infor.IMAGE_PATTERN, content)

            if m is None:
                return None

            url = getMatchString(m.group(0), Infor.MARK_PATTERN)
            return url

        return None

    def getSlogan(self):

        path = OutputPath.getDataPath(self.skuid, 'html')
        url = Infor.SKU_MAIN_URL_TEMPLATE.format(self.skuid)

        ret = Network.saveGetUrl(path, url)

        if ret < 0:
            return None

        with open(path) as fp:
            content = fp.read()

            slogan = getMatchString(content, Infor.SLOGAN_PATTERN)
            if slogan is not None and not isinstance(slogan, unicode):
                slogan = unicode(slogan, errors='ignore')
            return slogan

        return None

    def getComments(self):

        url = Infor.COMMENT_URL_TEMPLATE.format(self.skuid)
        path = OutputPath.getDataPath(self.skuid, 'json')

        ret = Network.saveGetUrl(path, url)

        if ret < 0:
            return None

        with open(path) as fp:
            content = fp.read()
            obj = json.loads(content)
            return obj.pop('wareDetailComment')

        return None

