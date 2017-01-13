import logging
import os
import sys
from unittest import TestCase
from unittest.mock import patch

import ca_analytics
from helpers import DbPatcherMixin

rwd = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
if rwd not in sys.path:
    sys.path.append(rwd)

log = logging.getLogger(__name__)


class TestOrderByEventsPresentInDB(DbPatcherMixin, TestCase):
    def setUp(self):
        self.patcher_get_ca_event_list = patch.object(ca_analytics,
                                                      'get_ca_event_list')

        # Start patch
        self.mock_get_ca_event_list = self.patcher_get_ca_event_list.start()
        super().setUp()

    def test_should_sort_events_by_event_id(self):
        pass

    def test_should_sort_events_by_start_time(self):
        pass

    def test_should_sort_users_by_display_name(self):
        pass

    def test_should_sort_users_by_join_time(self):
        pass


class TestOrderByEventsNotInDB(DbPatcherMixin, TestCase):
    def setUp(self):
        self.patcher_get_ca_event_list = patch.object(ca_analytics,
                                                      'get_ca_event_list')

        # Start patch
        self.mock_get_ca_event_list = self.patcher_get_ca_event_list.start()
        super().setUp()

    def test_should_assign_first_join_timestamp_as_event_start(self):
        pass

    def test_should_assign_last_join_timestamp_as_event_end(self):
        pass
