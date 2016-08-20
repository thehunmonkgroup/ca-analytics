#!/usr/bin/env python3
# (c) 2016 Alek
#  Proxy for getting relevant info from databases

import logging

from pymongo import MongoClient

from lib.extras import Setts

log = logging.getLogger(__name__)


class MongoData:
    _filter_join_events = {'action': 'join', 'message': 'events'}

    def __init__(self, connection_string, database_name):
        self._client = MongoClient(connection_string)
        self.db_mongo = self._client[database_name]

    def filter_date(self, date_from, date_to):
        pass

    def get_data(self, event_ids=None, user_ids=None):
        """
        Get data about specific events or users.

        :param user_ids:
        :param user_ids: list of userIds
        :type event_ids: list of eventIds
        :return:
        """
        question = self.filter_join_events

        if event_ids is not None:
            question["eventId"] = self._search_in(event_ids)
        if user_ids is not None:
            question["userId"] = self._search_in(user_ids, cast=str)

        ret = self.db_mongo.analytics.find(question)
        return ret

    @property
    def filter_join_events(self):
        return self._filter_join_events.copy()

    @staticmethod
    def _search_in(iterable, cast=int):
        """
        Return dict that will allow several fields to be searched against.
        DB is type (str, int, ..) sensitive.

        with userId:
        OverflowError: MongoDB can only handle up to 8-byte ints
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
    Setts._DB_MONGO.value = MongoData(
        connection_string=Setts.MONGO_STRING.value,
        database_name=Setts.MONGO_DATABASE.value
    )
