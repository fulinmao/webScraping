from datetime import timedelta, datetime

from pymongo import MongoClient


class MongoCache:
    def __init__(self,client=None ,max_length = 255, expires=timedelta(days=30)):
        # if a client object is not passed then try connecting to mongodb at the default localhost port
        self.client = MongoClient('localhost',27017) if client is None else client

        # create collection to store cached webpages
        # which is the equivalent of a table in a relational database
        self.db = client.cache

        # create index to expire cached webpages
        self.db.webpage.create_index('timestamp',expireAfterSeconds=expires.total_seconds())

    def __getitem__(self, url):
        """
        Load value at this URL
        :param url:
        :return:
        """
        record = self.db.webpage.find_one({'_id':url})

        if record:
            return record['result']
        else:
            raise KeyError(url + 'does not exist')

    def __setitem__(self, url, result):
        """
        Save the value for this URL
        :param url:
        :param result:
        :return:
        """
        record = {'result':result , 'timestamp':datetime.utcnow()}

        self.db.webpage.update({'_id':url},{'$set':record},upsert=True)