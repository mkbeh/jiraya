# -*- coding: utf-8 -*-

import json

from contextlib import contextmanager

from pymongo import MongoClient, errors
from pymongo import ReturnDocument
from bson.objectid import ObjectId


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class MongoDB(object):
    def __init__(self, db_name):
        try:
            cxn = MongoClient()
        except errors.AutoReconnect:
            raise RuntimeError()

        self.db = cxn[db_name]
        self.collection = None

    def db_dump(self):
        pass

    def find(self, data, collection_name, limit=0, skip=0):
        self.collection = self.db[collection_name]

        return [item for item in self.collection.find(data).skip(skip).limit(limit)]

    def find_one(self, data, collection_name):
        self.collection = self.db[collection_name]

        return self.collection.find_one(data)

    def find_one_by_id(self, obj_id, collection_name):
        self.collection = self.db[collection_name]

        # Convert from string to ObjectId and return.
        return self.collection.find_one({'_id': ObjectId(obj_id)})

    def find_one_and_update(self, filter_, data, collection_name, *args):
        self.collection = self.db[collection_name]

        for arg in args:
            if arg == '$set':
                return self.collection.find_one_and_update(filter_, {'$set': data}, upsert=True,
                                                           return_document=ReturnDocument.AFTER)

            elif arg == '$inc':
                return self.collection.find_one_and_update(filter_, {'$inc': data}, upsert=True,
                                                           return_document=ReturnDocument.AFTER)

    def find_one_and_update_by_id(self, obj_id, data, collection_name, *args):
        self.collection = self.db[collection_name]

        for arg in args:
            if arg == '$set':
                return self.collection.find_one_and_update({'_id': ObjectId(obj_id)}, {'$set': data}, upsert=True,
                                                           return_document=ReturnDocument.AFTER)

            elif arg == '$inc':
                return self.collection.find_one_and_update({'_id': ObjectId(obj_id)}, {'$inc': data}, upsert=True,
                                                           return_document=ReturnDocument.AFTER)

    def find_one_and_delete(self, filter_, collection_name, *args):
        self.collection = self.db[collection_name]

        for arg in args:
            if arg == '$set':
                return self.collection.find_one_and_delete(filter_, collection_name)

            elif arg == '$inc':
                return self.collection.find_one_and_update(filter_, collection_name)

    @contextmanager
    def insert_one(self, data, collection_name):
        self.collection = self.db[collection_name]
        s = self.collection.insert_one(data)
        self.finish()

        return s

    def delete_one(self, filter_, collection_name):
        self.collection = self.db[collection_name]

        self.collection.delete_one(filter_)

        return True

    def count(self, collection_name):
        self.collection = self.db[collection_name]

        return self.collection.count()

    def count_with_filter(self, filter_, collection_name):
        self.collection = self.db[collection_name]

        return self.collection.count(filter_)

    def finish(self):
        self.db.logout()
