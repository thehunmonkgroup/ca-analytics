import logging
import os
import sys
from unittest import TestCase
from unittest.mock import patch

import ca_analytics
from example_data import Event111, Event222, Event333, EventNoCouchData
from helpers import DbPatcherMixin

rwd = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
if rwd not in sys.path:
    sys.path.append(rwd)

log = logging.getLogger(__name__)


class TestOrderByEventsPresentInDB(DbPatcherMixin, TestCase):
    def setUp(self):
        self.patcher_output_handler = patch.object(ca_analytics,
                                                   'OutputHandler')
        self.mock_output_handler = self.patcher_output_handler.start()

        super().setUp()

    def test_should_sort_events_by_event_id(self):
        # GIVEN
        expected_events_sorted_by_event_id = [Event111, Event222, Event333]

        cli_cmd = '-e %s --order_by event_id' % ' '.join(
            [str(evnt.eventId) for evnt in expected_events_sorted_by_event_id])
        cli_cmd = cli_cmd.split()

        # WHEN
        ca_analytics.main(start_cmd=cli_cmd)

        # THEN
        ca_events = self.get_script_processed_data()
        self.check_if_events_valid(
            script_events_data=ca_events,
            expected_events_data=expected_events_sorted_by_event_id)

    def test_should_sort_events_by_start_time(self):
        # GIVEN
        expected_events = [Event111, Event222, Event333]
        expected_events_sorted_by_start_time = [Event333, Event111, Event222]

        cli_cmd = '-e %s --order_by start_time' % ' '.join(
            [str(evnt.eventId) for evnt in expected_events])
        cli_cmd = cli_cmd.split()

        # WHEN
        ca_analytics.main(start_cmd=cli_cmd)

        # THEN
        ca_events = self.get_script_processed_data()
        self.check_if_events_valid(
            script_events_data=ca_events,
            expected_events_data=expected_events_sorted_by_start_time)

    def test_should_sort_users_by_display_name(self):
        # GIVEN
        expected_event = Event111.eventId

        cli_cmd = '-e %s --order_by display_name' % expected_event
        cli_cmd = cli_cmd.split()

        # WHEN
        ca_analytics.main(start_cmd=cli_cmd)

        # THEN
        ca_events = self.get_script_processed_data()
        self.check_if_participants_in_alphabetical_order(ca_events=ca_events)

    def test_should_sort_users_by_join_time(self):
        # GIVEN
        expected_event = Event111.eventId

        cli_cmd = '-e %s --order_by join_time' % expected_event
        cli_cmd = cli_cmd.split()

        # WHEN
        ca_analytics.main(start_cmd=cli_cmd)

        # THEN
        ca_events = self.get_script_processed_data()
        self.check_if_participants_in_join_order(ca_events=ca_events)


class TestOrderByEventsNotInDB(DbPatcherMixin, TestCase):
    # Maybe this is not strictly unit test, cos it checks user timestamp and
    #   event start/end time at the same time if those matches example data

    # TODO: Is it not cloning tests from test_events_and_users ?

    # TODO: events now will take all_timestamps as first or last timestamp TEST

    def setUp(self):
        self.patcher_output_handler = patch.object(ca_analytics,
                                                   'OutputHandler')
        self.mock_output_handler = self.patcher_output_handler.start()

        super().setUp()

    def test_should_assign_first_join_timestamp_as_event_start(self):
        # GIVEN
        expected_event = EventNoCouchData
        expected_start_time = self.get_events_first_user_timestamp(
            EventNoCouchData).join

        cli_cmd = '-e %s' % expected_event.eventId
        cli_cmd = cli_cmd.split()

        # WHEN
        ca_analytics.main(start_cmd=cli_cmd)

        # THEN
        ca_event = self.get_script_processed_data()[0]
        timestamps = ca_event._participants_handler.join_timestamps

        event_start_time = ca_event.start_time
        first_participant_timestamp = timestamps[0]

        self.assertEqual(expected_start_time, event_start_time)
        self.assertEqual(expected_start_time, first_participant_timestamp)

    def test_should_assign_last_leave_timestamp_as_event_end(self):
        # GIVEN
        expected_event = EventNoCouchData
        expected_end_time = self.get_events_first_user_timestamp(
            EventNoCouchData).leave

        cli_cmd = '-e %s' % expected_event.eventId
        cli_cmd = cli_cmd.split()

        # WHEN
        ca_analytics.main(start_cmd=cli_cmd)

        # THEN
        ca_event = self.get_script_processed_data()[0]
        timestamps = ca_event._participants_handler.leave_timestamps

        event_end_time = ca_event.end_time
        last_participant_timestamp = timestamps[-1]

        self.assertEqual(expected_end_time, last_participant_timestamp)
        self.assertEqual(expected_end_time, event_end_time)
