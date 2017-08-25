import httplib  
import os
import random
import socket
import time

class Network:

    _instance = None

    def __init__(self):
        self.isLocal = True

    @staticmethod
    def setIsLocal(isLocal):

        if Network._instance is None:
            Network._instance = Network()

        Network._instance.isLocal = isLocal

    @staticmethod
    def saveHttpData(pathname, url, host=None):

        if Network._instance is None:
            Network._instance = Network()

        ret = Network._instance.saveHttpDataImpl(pathname, url, host)

        # Sleep for a while
        time.sleep(random.random())

        return ret

    def saveHttpDataImpl(self, pathname, url, host):

        if self.isLocal and os.path.exists(pathname):
            return 0

        if None == host:
            start = url.find('//') + 2
            end = url[start:].find('/')

            host = url[start:start+end]
            url = url[start+end:]

        for i in range(0, 3):
            conn = httplib.HTTPConnection(host, timeout=10)  

            try:
                conn.request("GET", url)
                res = conn.getresponse()

                if 200 != res.status:
                    print res.status, res.reason
                    continue

                data = res.read()

            except Exception:
                print 'Timeout, try it again. NO. ', i+1

                # Sleep a while
                time.sleep(30 * i)
                continue

            finally:
                conn.close()

            fp = open(pathname, 'w')
            fp.write(data)
            fp.close()

            return 0

        return -1

