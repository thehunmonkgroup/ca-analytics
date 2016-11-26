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
from example_data import ResponseFactory, Event111, Event222
from lib.db_engine import MongoData, CouchData

rwd = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
if rwd not in sys.path:
    sys.path.append(rwd)

log = logging.getLogger(__name__)


class TestMain(unittest.TestCase):
    # TODO: Fail with: 00494, 00323: No event for id [00494] found in CouchDB
    # TODO: Test for select event&user
    # TODO: Test for show users' events
    # TODO: *Test for correct date from/to limits
    # TODO: *Test all script switches ?

    get_expected_users = ResponseFactory.get_users_for_given_event_class

    def setUp(self):
        self.patcher_output_handler = patch.object(ca_analytics,
                                                   'OutputHandler')

        self.patcher_coach_get_data = patch.object(CouchData, 'get_data',
                                                   side_effect=ResponseFactory.couch_get_data_side_effect)
        self.patcher_coach_init = patch.object(CouchData, '__init__',
                                               return_value=None)

        self.patcher_mongo_get_data = patch.object(MongoData, 'get_data',
                                                   side_effect=ResponseFactory.mongo_get_data_side_effect)
        self.patcher_mongo_init = patch.object(MongoData, '__init__',
                                               return_value=None)

        # Start patch
        self.mock_output_handler = self.patcher_output_handler.start()

        self.mock_coach_get_data = self.patcher_coach_get_data.start()
        self.mock_coach_init = self.patcher_coach_init.start()

        self.mock_mongo_get_data = self.patcher_mongo_get_data.start()
        self.mock_mongo_init = self.patcher_mongo_init.start()

        # Stop patch
        self.addCleanup(patch.stopall)

        # How to get to script data:
        # print(self.mock_mongo_init.call_args_list)
        # print(self.mock_mongo_get_data.call_args_list)
        # print(self.mock_coach_init.call_args_list)
        # print(self.mock_coach_get_data.call_args_list)
        # print(self.mock_output_handler.call_args_list)

    def test_should_select_all_users_attending_the_event(self):
        # GIVEN
        expected_event = Event111
        expected_events = [Event111]
        expected_users = self.get_expected_users(event_list=expected_events)

        cli_cmd = '-e %s' % expected_event.eventId
        cli_cmd = cli_cmd.split()

        # WHEN
        main(start_cmd=cli_cmd)

        # THEN
        ca_events = self.get_script_processed_data()

        self.check_if_events_valid(script_events_data=ca_events,
                                   expected_events_data=expected_events)

        # TODO: Move to check_if_users_valid(ca_events, expected_events)
        for ca_event, expected_event in zip(ca_events, expected_events):
            self.check_if_users_valid(
                script_events_users=ca_event.event_users,
                expected_events_users=expected_users[expected_event],
                event_id=expected_event.eventId
            )

    def test_should_get_data_about_two_events(self):
        # GIVEN
        expected_events = [Event111, Event222]
        expected_users = self.get_expected_users(event_list=expected_events)

        cli_cmd = '-e %s' % ' '.join([str(e.eventId) for e in expected_events])
        cli_cmd = cli_cmd.split()

        # WHEN
        main(start_cmd=cli_cmd)

        # THEN
        ca_events = self.get_script_processed_data()

        self.check_if_events_valid(script_events_data=ca_events,
                                   expected_events_data=expected_events)

        for ca_event, expected_event in zip(ca_events, expected_events):
            self.check_if_users_valid(
                script_events_users=ca_event.event_users,
                expected_events_users=expected_users[expected_event],
                event_id=expected_event.eventId
            )

    def get_script_processed_data(self):
        """
        This data is processed by the script, right before being displayed.

        :return:
        """
        ca_events = self.mock_output_handler.call_args[1]['ca_events_list']
        return ca_events

    def check_if_events_valid(self, script_events_data, expected_events_data):
        """
        Output will be sorted by id number, so expected events should also be
         added in order.

        :param script_events_data:
        :param expected_events_data:
        :return:
        """
        self.assertEqual(len(script_events_data), len(expected_events_data))

        events = (script_events_data, expected_events_data)
        for ca_event, expected_event in zip(*events):
            self.assertEqual(ca_event.event_id, expected_event.eventId)
            self.assertEqual(ca_event.description, expected_event.description)
            self.assertEqual(ca_event.calendar_id, expected_event.calendar_id)
            self.assertEqual(ca_event.start_time, expected_event.start_time)

    def check_if_users_valid(self, script_events_users, expected_events_users,
                             event_id):
        self.assertEqual(len(script_events_users), len(expected_events_users))

        for user in script_events_users:
            # Dunno in which order it was added to sample data
            expected_user = [u for u in expected_events_users
                             if u.userId == user.user_id][0]

            self.assertEqual(user.user_id, expected_user.userId)
            self.assertEqual(user.display_name, expected_user.display_name)
            self.assertEqual(
                user.timestamp,
                expected_user.get_earliest_timestamp(event_id=event_id),
                msg='Timestamps mismatch. User was logged earlier!'
            )


if __name__ == '__main__':
    unittest.main()