import os
import random
import requests
import time

from utils import chmod

class Network:

    _instance = None
    timeout = 10

    def __init__(self):
        self.isLocal = True

    @staticmethod
    def setIsLocal(isLocal):

        if Network._instance is None:
            Network._instance = Network()

        Network._instance.isLocal = isLocal

    @staticmethod
    def get(url, params=None, retries=1, **kwargs):

        for i in range(retries):
            try:
                return requests.get(url, params=params, timeout=Network.timeout, **kwargs)
            except Exception as e:
                print 'Error to get', url, ':', e

            if i > 0:
                # Sleep a while
                time.sleep(30 * i)

        return None

    @staticmethod
    def post(url, data=None, json=None, **kwargs):

        try:
            return requests.post(url, data=data, json=json, **kwargs)
        except Exception as e:
            print 'Error to post', url, ':', e

        return None

    @staticmethod
    def getUrl(url, params=None, headers=None, retries=1):

        if Network._instance is None:
            Network._instance = Network()

        content = Network._instance.getUrlImpl(url, params, headers, retries)

        # Sleep for a while
        if content is not None:
            time.sleep(random.random())

        return content

    def getUrlImpl(self, url, params, headers, retries):

        r = Network.get(url, params=params, headers=headers, retries=retries)

        if r is None:
            return ''

        # TODO: add other judgement for http response
        return r.text

    @staticmethod
    def saveGetUrl(pathname, url, force=False, retries=1):

        if Network._instance is None:
            Network._instance = Network()

        ret = Network._instance.saveGetUrlImpl(pathname, url, force, retries)

        # Sleep for a while
        if ret is 0:
            print 'Updated', pathname
            time.sleep(random.random())

        return ret

    def saveGetUrlImpl(self, pathname, url, force, retries):

        if not force and self.isLocal and os.path.exists(pathname):
            return 1

        r = Network.get(url, retries=retries)
        if r is None:
            return -1

        # TODO: add other judgement for http response

        with open(pathname, 'wb') as fp:
            fp.write(r.content)

        chmod(pathname)

        return 0

