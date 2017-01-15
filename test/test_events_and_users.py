import logging
import os
import sys
from unittest import TestCase
from unittest import skip
from unittest.mock import patch

import ca_analytics
from ca_analytics import main
from example_data import Event111, Event222, User111, \
    EventIncompleteUsersTimestamps, UserNoLeaveTimeLogs, UserNoJoinTimeLogs
from helpers import ResponseFactory, DbPatcherMixin

rwd = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
if rwd not in sys.path:
    sys.path.append(rwd)

log = logging.getLogger(__name__)


class TestUser(DbPatcherMixin, TestCase):
    get_expected_users = ResponseFactory.get_users_for_given_event_class

    def setUp(self):
        self.patcher_output_handler = patch.object(ca_analytics,
                                                   'OutputHandler')

        # Start patch
        self.mock_output_handler = self.patcher_output_handler.start()

        super().setUp()
        # How to get to script data:
        # print(self.mock_mongo_init.call_args_list)
        # print(self.mock_mongo_get_data.call_args_list)
        # print(self.mock_coach_init.call_args_list)
        # print(self.mock_coach_get_data.call_args_list)

    def test_should_select_events_user_participated(self):
        # GIVEN
        user = User111
        expected_event_ids = [mongo_log.event_id for mongo_log
                              in User111._participated_in]

        cli_cmd = '-u %s' % user.userId
        cli_cmd = cli_cmd.split()

        # WHEN
        main(start_cmd=cli_cmd)

        # THEN
        ca_events = self.get_script_processed_data()
        actual_event_ids = [ca_event.event_id for ca_event in ca_events]

        self.assertEqual(expected_event_ids, actual_event_ids)

    def test_should_select_user_and_event_he_participated(self):
        # GIVEN
        user = User111
        expected_event = Event111

        cli_cmd = '-u %s -e %s' % (user.userId, expected_event.eventId)
        cli_cmd = cli_cmd.split()

        # WHEN
        main(start_cmd=cli_cmd)

        # THEN
        ca_events = self.get_script_processed_data()

        self.assertTrue(len(ca_events) == 1)
        self.assertEqual(expected_event.eventId, ca_events[0].event_id)


class TestEvent(DbPatcherMixin, TestCase):
    def setUp(self):
        self.patcher_output_handler = patch.object(ca_analytics,
                                                   'OutputHandler')

        # Start patch
        self.mock_output_handler = self.patcher_output_handler.start()

        super().setUp()
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
                script_events_users=ca_event.event_participants(),
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
                script_events_users=ca_event.event_participants(),
                expected_events_users=expected_users[expected_event],
                event_id=expected_event.eventId
            )


class TestTimestamps(DbPatcherMixin, TestCase):
    def setUp(self):
        self.patcher_output_handler = patch.object(ca_analytics,
                                                   'OutputHandler')
        self.mock_output_handler = self.patcher_output_handler.start()

        super().setUp()

    def test_should_return_none_when_no_leave_timestamp(self):
        # GIVEN
        expected_user = UserNoLeaveTimeLogs

        cli_cmd = '-u %s' % expected_user.userId
        cli_cmd = cli_cmd.split()

        # WHEN
        ca_analytics.main(start_cmd=cli_cmd)

        # THEN
        ca_events = self.get_script_processed_data()
        participant = ca_events[0].event_participants()[0]

        self.assertIsNone(participant.timestamp.leave)

    def test_should_return_none_when_no_join_timestamp(self):
        # GIVEN
        expected_user = UserNoJoinTimeLogs

        cli_cmd = '-u %s' % expected_user.userId
        cli_cmd = cli_cmd.split()

        # WHEN
        ca_analytics.main(start_cmd=cli_cmd)

        # THEN
        ca_events = self.get_script_processed_data()
        participant = ca_events[0].event_participants()[0]

        self.assertIsNone(participant.timestamp.join)

    def test_should_assign_first_date_ever_for_no_event_in_db(self):
        test_users = []

    # def test_should_assign_last_join_timestamp_as_event_end(self):
    #     # GIVEN
    #     expected_event = EventEmpty
    #
    #     cli_cmd = '-e %s --order_by event_id' % expected_event.eventId
    #     cli_cmd = cli_cmd.split()
    #
    #     # WHEN
    #     ca_analytics.main(start_cmd=cli_cmd)
    #
    #     # THEN
    #     ca_event = self.get_script_processed_data()[0]
    #     timestamps = ca_event._participants_handler.join_timestamps
    #
    #     event_end_time = ca_event.end_time
    #     last_participant_timestamp = timestamps[-1]
    #
    #     self.assertEqual(last_participant_timestamp, event_end_time)

# class TestEventDates(DbPatcherMixin, TestCase):
#     def setUp(self):
#         self.patcher_output_handler = patch.object(ca_analytics,
#                                                    'OutputHandler')
#         self.mock_output_handler = self.patcher_output_handler.start()
#
#         super().setUp()
#
#     def test_should_assign_first_join_timestamp_as_event_start(self):
#         # GIVEN
#         expected_event = EventEmpty
#
#         cli_cmd = '-e %s --order_by event_id' % expected_event.eventId
#         cli_cmd = cli_cmd.split()
#
#         # WHEN
#         ca_analytics.main(start_cmd=cli_cmd)
#
#         # THEN
#         ca_event = self.get_script_processed_data()[0]
#         timestamps = ca_event._participants_handler.get_join_timestamps()
#
#         event_start_time = ca_event.start_time
#         first_participant_timestamp = timestamps[0]
#
#         self.assertEqual(first_participant_timestamp, event_start_time)
#
#     def test_should_assign_last_join_timestamp_as_event_end(self):
#         # GIVEN
#         expected_event = EventEmpty
#
#         cli_cmd = '-e %s --order_by event_id' % expected_event.eventId
#         cli_cmd = cli_cmd.split()
#
#         # WHEN
#         ca_analytics.main(start_cmd=cli_cmd)
#
#         # THEN
#         ca_event = self.get_script_processed_data()[0]
#         timestamps = ca_event._participants_handler.get_join_timestamps()
#
#         event_end_time = ca_event.end_time
#         last_participant_timestamp = timestamps[-1]
#
#         self.assertEqual(last_participant_timestamp, event_end_time)
