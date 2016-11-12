#!/usr/bin/env python3
# (c) 2016 Alek
#  Integrations test for Circle Anywhere

import logging
import os
import sys
import unittest
from unittest.mock import patch

import ca_analytics
from ca_analytics import main
from example_data import ResponseFactory, Event111
from lib.db_engine import MongoData, CouchData

rwd = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
if rwd not in sys.path:
    sys.path.append(rwd)

log = logging.getLogger(__name__)


class TestMain(unittest.TestCase):
    # TODO: # Fail with: 00494, 00323: No event for id [00494] found in CouchDB

    @patch.object(ca_analytics, 'OutputHandler')
    @patch.object(CouchData, 'get_data',
                  side_effect=ResponseFactory.couch_get_data_side_effect)
    @patch.object(CouchData, '__init__', return_value=None)
    @patch.object(MongoData, 'get_data',
                  side_effect=ResponseFactory.mongo_get_data_side_effect)
    @patch.object(MongoData, '__init__', return_value=None)
    def test_should_select_all_users_attending_the_event(
            self, mock_mongo_init, mock_db_mongo, mock_coach_init,
            mock_coach_db, mock_output_handler):
        # Given
        expected_event = Event111
        cli_cmd = '-e %s' % expected_event.eventId
        cli_cmd = cli_cmd.split()

        # When
        main(start_cmd=cli_cmd)

        # Then
        # print(mock_mongo_init.call_args_list)
        # print(mock_db_mongo.call_args_list)
        # print(mock_coach_init.call_args_list)
        # print(mock_coach_db.call_args_list)
        # print(mock_output_handler.call_args_list)
        ca_event = mock_output_handler.call_args[1]['ca_events_list'][0]

        # Check if correct event
        self.assertEqual(ca_event.event_id, expected_event.eventId)
        self.assertEqual(ca_event.description, expected_event.description)
        self.assertEqual(ca_event.calendar_id, expected_event.calendar_id)
        self.assertEqual(ca_event.start_time, expected_event.start_time)

        # Check if correct users
        expected_users = ResponseFactory.get_all_users_attending_event(
            event_id=ca_event.event_id)
        self.assertEqual(len(ca_event.event_users), len(expected_users))
        for user in ca_event.event_users:
            expected_user = [u for u in expected_users
                             if u.userId == user.user_id][0]

            self.assertEqual(user.user_id, expected_user.userId)
            self.assertEqual(user.display_name, expected_user.display_name)
            self.assertEqual(user.timestamp,
                             expected_user.get_earliest_timestamp(
                                 event_id=ca_event.event_id),
                             msg='Timestamps mismatch. User was logged earlier!')


if __name__ == '__main__':
    unittest.main()
