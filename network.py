import httplib  
import socket
import time

def saveHttpData(filename, url, host=None):

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

        fp = open(filename, 'w')
        fp.write(data)
        fp.close()

        return 0

    return -1

