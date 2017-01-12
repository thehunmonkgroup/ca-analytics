import logging
import os
import sys
import unittest
from unittest.mock import patch

import ca_analytics
from helpers import ResponseFactory
from lib.database import MongoData, CouchData
from lib.extras import Setts

rwd = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
if rwd not in sys.path:
    sys.path.append(rwd)

log = logging.getLogger(__name__)


class TestEventsInCouchDB(unittest.TestCase):
    def setUp(self):
        self.patcher_get_ca_event_list = patch.object(ca_analytics,
                                                      'get_ca_event_list')

        self.patcher_coach_get_data = patch.object(CouchData, 'get_data',
                                                   side_effect=ResponseFactory.couch_get_data_side_effect)
        self.patcher_coach_init = patch.object(CouchData, '__init__',
                                               return_value=None)

        self.patcher_mongo_get_data = patch.object(MongoData, 'get_data',
                                                   side_effect=ResponseFactory.mongo_get_data_side_effect)
        self.patcher_mongo_init = patch.object(MongoData, '__init__',
                                               return_value=None)

        # Start patch
        self.mock_get_ca_event_list = self.patcher_get_ca_event_list.start()

        self.mock_coach_get_data = self.patcher_coach_get_data.start()
        self.mock_coach_init = self.patcher_coach_init.start()

        self.mock_mongo_get_data = self.patcher_mongo_get_data.start()
        self.mock_mongo_init = self.patcher_mongo_init.start()

        # Stop patch
        self.addCleanup(patch.stopall)

        Setts.refresh(reset=True)

    def test_should_sort_events_by_event_id(self):
        pass

    def test_should_sort_events_by_start_time(self):
        pass

    def test_should_sort_users_by_display_name(self):
        pass

    def test_should_sort_users_by_join_time(self):
        pass


class TestEventsNotInCouchDB(unittest.TestCase):
    def setUp(self):
        self.patcher_get_ca_event_list = patch.object(ca_analytics,
                                                      'get_ca_event_list')

        self.patcher_coach_get_data = patch.object(CouchData, 'get_data',
                                                   side_effect=ResponseFactory.couch_get_data_side_effect)
        self.patcher_coach_init = patch.object(CouchData, '__init__',
                                               return_value=None)

        self.patcher_mongo_get_data = patch.object(MongoData, 'get_data',
                                                   side_effect=ResponseFactory.mongo_get_data_side_effect)
        self.patcher_mongo_init = patch.object(MongoData, '__init__',
                                               return_value=None)

        # Start patch
        self.mock_get_ca_event_list = self.patcher_get_ca_event_list.start()

        self.mock_coach_get_data = self.patcher_coach_get_data.start()
        self.mock_coach_init = self.patcher_coach_init.start()

        self.mock_mongo_get_data = self.patcher_mongo_get_data.start()
        self.mock_mongo_init = self.patcher_mongo_init.start()

        # Stop patch
        self.addCleanup(patch.stopall)

        Setts.refresh(reset=True)

    def test_should_assign_first_join_timestamp_as_event_start(self):
        pass

    def test_should_assign_last_join_timestamp_as_event_end(self):
        pass
