# Utils
import binascii
import cStringIO
import json
import os
import pprint
import re
import requests
import sys
import subprocess
import threading
import time
import traceback

from datetime import tzinfo, timedelta, datetime
from network import Network

def seconds2Datetime(seconds):
    #return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(seconds))
    return datetime.fromtimestamp(seconds).strftime('%Y-%m-%d %H:%M:%S')

def getchar():
    print 'Please press return key to continue'
    sys.stdin.read(1)

def toVisibleAscll(src):

    if None == src or 0 == len(src):
        return src

    if unicode != type(src):
        try:
            src = unicode(src, errors='ignore')
        except TypeError, e:
            print 'Unable to translate {!r} of type {}'.format(src, type(src)), ':', e

    dest = ''

    for char in src:
        if char < unichr(32): continue
        dest += char

    return dest

def hexlifyUtf8(src):
    return binascii.hexlify(src.encode('utf-8', 'ignore'))

def unhexlifyUtf8(src):
    return binascii.unhexlify(src).decode('utf-8', 'ignore')

def runProcess(cmd, onlyFirstLine=True):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    if onlyFirstLine:
        ret = p.wait()
        if 0 != ret: raise IndexError, 'Unable to run "{}"'.format(cmd)
        for line in p.stdout.readlines():
            return line.rstrip('\r').rstrip('\n')
    else:
        return p.stdout.read()

# update property of name to value
def updateProperty(path, name, value):
    fp = None
    targetLine = None
    newLine = None
    try:
        fp = open(path)
        minlen = len(name) + 1
        for line in fp:
            if len(line) < minlen or '#' == line[0]:
                continue
            group = line.strip().split('=')
            if 2 != len(group) or group[0].strip() != name:
                continue
            if group[1] == value:
                return None
            else:
                targetLine = line
                newLine = '{}={}\r\n'.format(name,value)
                break
    except IOError:
        pass
    finally:
        if fp != None: fp.close()

    if targetLine != None and newLine != None:
        with open(path) as fp:
            content = fp.read()

        content = content.replace(targetLine, newLine)

        with open(path, 'w') as fp:
            fp.write(content)

    return None

def getProperty(path, name):

    fp = None

    try:
        fp = open(path)

        minlen = len(name) + 1

        for line in fp:
            if len(line) < minlen or '#' == line[0]:
                continue

            line = line.strip()
            pos = line.find('=')

            if pos < 0:
                continue

            if line[:pos] != name:
                continue

            return line[pos+1:].strip()

    except IOError:
        pass

    finally:
        if fp != None: fp.close()

    return None

def safePop(obj, name, defaultValue=None):

    try:
        return obj.pop(name)
    except KeyError:
        pass

    return defaultValue

def getMatchString(content, pattern):

    matches = re.findall(pattern, content)

    if matches is None or 0 == len(matches):
        return None

    return matches[0]

def dump(obj):

    def dumpObj(obj):

        fields = ['    {}={}'.format(k, v)
            for k, v in obj.__dict__.items() if not k.startswith('_')]

        return ' {}:\n{}'.format(obj.__class__.__name__, '\n'.join(fields))

    if obj is None: return None

    if type(obj) is list:

        for subObj in obj:
            dump(subObj)
    else:
        print dumpObj(obj)

def reprDict(data):
    return json.dumps(data, ensure_ascii=False, indent=4, sort_keys=True)

def printDict(obj):
    UniPrinter().pprint(obj)

class UniPrinter(pprint.PrettyPrinter):

    def format(self, obj, context, maxlevels, level):

        if isinstance(obj, unicode):

            out = cStringIO.StringIO()
            out.write('u"')

            for c in obj:
                if ord(c) < 32 or c in u'"\\':
                    out.write('\\x%.2x' % ord(c))
                else:
                    out.write(c.encode("utf-8"))

            out.write('"''"')

            # result, readable, recursive
            return out.getvalue(), True, False

        if isinstance(obj, str):

            out = cStringIO.StringIO()
            out.write('"')

            for c in obj:
                if ord(c) < 32 or c in '"\\':
                    out.write('\\x%.2x' % ord(c))
                else:
                    out.write(c)

            out.write('"')

            # result, readable, recursive
            return out.getvalue(), True, False

        return pprint.PrettyPrinter.format(self, obj,
            context, maxlevels, level)

class AutoReleaseThread(threading.Thread):

    def __init__(self):

        self.isInitialized = False

        self.running = True
        threading.Thread.__init__(self)

        self.mutex = threading.Lock()

    def initialize(self):

        try:
            self.mutex.acquire()

            if not self.isInitialized:

                self.isInitialized = True

                self.onInitialized()

            self.accessTime = time.time()

        except KeyboardInterrupt:
            raise KeyboardInterrupt

        finally:
            self.mutex.release()

    def release(self):

        self.isInitialized = False

        self.onReleased()

    def run(self):

        threadname = threading.currentThread().getName()

        while self.running:

            self.mutex.acquire()

            if self.isInitialized:

                diff = time.time() - self.accessTime

                if diff > 30: # 30 seconds
                    self.release()

            self.mutex.release()

            time.sleep(1)

        else:
            self.release()

        print 'Quit'

    def quit(self):

        print 'Stopping ...'
        self.running = False

class ThreadWritableObject(threading.Thread):

    def __init__(self, configFile):

        threading.Thread.__init__(self)

        self.running = True

        outputPath = getProperty(configFile, 'output-path')
        outputPath = os.path.realpath(outputPath)
        outputPath = os.path.join(outputPath, 'logs')

        if not os.path.exists(outputPath):
            os.mkdir(outputPath, 0755)

        self.path = os.path.join(outputPath, 'sys.log')
        self.contents = []

        self.mutex = threading.Lock()

    def write(self, content):

        self.mutex.acquire()

        self.contents.append(content)

        self.mutex.release()

    def run(self):

        def output(path, contents):

            with open(path, 'a') as fp:

                for content in contents:
                    fp.write(content)

        threadname = threading.currentThread().getName()

        while self.running:

            self.mutex.acquire()

            if 0 != len(self.contents):

                MAX_SIZE = 2*1024*1024

                if os.path.exists(self.path) and os.stat(self.path).st_size > MAX_SIZE:

                    os.rename(self.path, '{}.old'.format(self.path))

                output(self.path, self.contents)

                del self.contents[:]

            self.mutex.release()

            time.sleep(10)

        else:
            output(self.path, self.contents)

    def quit(self):

        print 'Quit ...'
        self.running = False

class UrlUtils:

    SHORT_URL_TRANSLATOR_URL = ''
    SHORT_URL_REFERER = ''
    SHORT_URL_USER_AGENT = ''
    SHORT_URL_SOURCE = ''
    SHORT_URL_CALLBACK = ''

    HTTP_URL_PATTERN = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    HTTP_SHORT_URL_PATTERN = r'(\w+://[\w\-\.]+(:(\d+)){0,1}/[\w]+)'

    @staticmethod
    def init(configFile):

        UrlUtils.SHORT_URL_TRANSLATOR_URL = getProperty(configFile, 'short-url-translator-url')

        UrlUtils.SHORT_URL_REFERER = getProperty(configFile, 'short-url-referer')
        UrlUtils.SHORT_URL_USER_AGENT = getProperty(configFile, 'short-url-user-agent')

        UrlUtils.SHORT_URL_SOURCE = getProperty(configFile, 'short-url-source')
        UrlUtils.SHORT_URL_CALLBACK = getProperty(configFile, 'short-url-callback')

    @staticmethod
    def toShortUrl(originalUrl):

        HEADERS = {
            'Referer': UrlUtils.SHORT_URL_REFERER,
            'User-Agent': UrlUtils.SHORT_URL_USER_AGENT
        }

        params = {'source': UrlUtils.SHORT_URL_SOURCE,
            'url_long': originalUrl,
            'callback': UrlUtils.SHORT_URL_CALLBACK}

        content = Network.getUrl(UrlUtils.SHORT_URL_TRANSLATOR_URL, params, HEADERS)

        start = content.find('(')
        end = content.rfind(')')

        if start < 0 or end < 0:
            return None

        obj = json.loads(content[start+1:end-1].decode('utf-8', 'ignore'))
        objs = obj.pop('urls')

        if objs is None or type(objs) is not list or 0 == len(objs):
            return None

        shortUrl = objs[0].pop('url_short')

        return shortUrl

    @staticmethod
    def toOriginalUrl(shortUrl):

        r = requests.get(shortUrl, allow_redirects=False)

        # HTTP 301: redirect(Permanently Moved)
        # HTTP 302: redirect(Temporarily Moved)
        if 301 == r.status_code or 302 == r.status_code:
            return r.headers['Location']

        return shortUrl

    @staticmethod
    def isShortUrl(url):
        return re.match(UrlUtils.HTTP_SHORT_URL_PATTERN, url) is not None

def removeOverdueFiles(pathname, seconds, suffix=None):

    now = time.time()

    for parent, dirnames, filenames in os.walk(pathname):

        for filename in filenames:

            path = parent + filename

            if None != suffix and not filename.endswith(suffix):
                continue

            if now > os.path.getctime(path) + seconds:
                # Remove
                os.remove(path)
