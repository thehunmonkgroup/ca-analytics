#!/usr/bin/env python3
# (c) 2016 Alek
#  Proxy for getting relevant info from databases

import logging

from pymongo import MongoClient

from lib.extras import Setts

log = logging.getLogger(__name__)


class MongoData:
    _base = {'action': 'join', 'message': 'events'}

    def __init__(self, connection_string, database_name):
        self._client = MongoClient(connection_string)
        self.db_mongo = self._client[database_name]

    def get_events(self, ids=None):
        question = self.base
        ret = self.db_mongo.analytics.find(question)
        return ret

    @property
    def base(self):
        return self._base.copy()

    @staticmethod
    def _search_in(iterable, cast=int):
        """
        Return dict that will allow several fields to be searched against.
        DB is type (str, int, ..) sensitive.
        """
        ret = []
        for each in iterable:
            try:
                ret.append(cast(each))
            except Exception as e:
                log.error('Could not convert value "%s" to type "%s"\n%s',
                          each, type(cast), e)
        return {'$in': ret}


def init_db():
    Setts.DB_MONGO.value = MongoData(
        connection_string=Setts.MONGO_STRING.value,
        database_name=Setts.MONGO_DATABASE.value
    )
