import dataset
import sqlalchemy
import MySQLdb

from utils import getProperty, toVisibleAscll, AutoReleaseThread

def toDbText(src):
    if None == src or 0 == len(src): return ''
    return src.replace('\'', '').replace('"', '')

class Database(AutoReleaseThread):

    def __init__(self, configFile, dbName):

        AutoReleaseThread.__init__(self)

        self.host = getProperty(configFile, 'mysql-host')
        self.username = getProperty(configFile, 'mysql-user')
        self.password = getProperty(configFile, 'mysql-password')

        self.enabled = False

        enabled = getProperty(configFile, 'db-enabled')

        if None != enabled:
            enabled = enabled.upper()
            if 'Y' == enabled or 'YES' == enabled:
                self.enabled = True

        self.dbName = dbName
        self.db = None

        if self.enabled:
            self.start()

    def onInitialized(self):

        if self.db is not None:
            return

        if self.connectDb():
            return 

        self.createDb()
        self.connectDb()

    def onReleased(self):

        if not self.enabled:
            return

        if self.db is None:
            return

        self.db.commit()
        self.db = None

    def createDb(self):

        conn = MySQLdb.connect(host=self.host, user=self.username, passwd=self.password)

        try:
            print 'Creating', self.dbName, 'in', self.host
            conn.cursor().execute('CREATE DATABASE IF NOT EXISTS {}'.format(self.dbName))
            print 'Created', self.dbName, 'in', self.host
        except MySQLdb.OperationalError as e:
            print 'Unable to create DB', self.dbName, 'in', self.host
        finally:
            conn.commit()
            conn.close()

    def connectDb(self):

        try:
            print 'Connecting', self.dbName, 'in', self.host
            self.db = dataset.connect('mysql://{}:{}@{}/{}'.format(self.username,
                self.password, self.host, self.dbName))
            print 'Connected', self.dbName, 'in', self.host
            return True

        except sqlalchemy.exc.OperationalError as e:
            return False

    def execute(self, sql):

        if not self.enabled: return True

        self.initialize()

        try:
            self.cursor.execute(sql)

        except Exception as e:
            print 'DATABASE ERROR (', e, '):', sql
            return False

        return True

    def insert(self, tableName, recordDict):

        if self.db is None:
            return

        table = self.db[tableName]
        table.insert(recordDict)

    def update(self, tableName, recordDict, keys):

        if self.db is None:
            return

        table = self.db[tableName]
        table.update(recordDict, keys)

    def query(self, sql):

        if self.db is None:
            return None

        try:
            return self.db.query(sql)
        except sqlalchemy.exc.ProgrammingError as e:
            print e

