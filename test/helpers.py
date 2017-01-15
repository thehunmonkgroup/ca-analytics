import logging
import os
import sys
from unittest.mock import patch

from example_data import Event111, Event222, Event333, UserNoLeaveTimeLogs, \
    UserNoJoinTimeLogs
from example_data import User111, User222, UserDateFilter
from lib.database import MongoData, CouchData
from lib.extras import Setts
from lib.extras import make_iterable

rwd = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
if rwd not in sys.path:
    sys.path.append(rwd)

log = logging.getLogger(__name__)


class ResponseFactory:
    NOT_CALLED = 'not called'
    sample_users = [
        User111,
        User222,
        UserDateFilter,
        UserNoLeaveTimeLogs,
        UserNoJoinTimeLogs,
    ]
    sample_events = [
        Event111,
        Event222,
        Event333,
    ]

    @classmethod
    def get_all_users_attending_event(cls, event_id):
        ret = []

        def user_attended(usr):
            for event_attended in usr._participated_in:
                if event_attended.event_id == event_id:
                    return True
            return False

        for user in cls.sample_users:
            if user_attended(user):
                ret.append(user)

        return ret

    @classmethod
    def get_users_for_given_event_class(cls, event_list):
        """
        Retrun dict:
            {Event_class: [User1, User2, ..], ...], Event_2: [], }
        :param event_list: List of Sample event class
        :return:
        """
        ret = {}
        for event_class in event_list:
            users = cls.get_all_users_attending_event(
                event_id=event_class.eventId)
            ret[event_class] = users
        return ret

    @classmethod
    def get_all_mongo_logs(cls):
        ret = []
        for sample_user in cls.sample_users:
            ret.extend(sample_user.get_mongo_response())
        return ret

    @classmethod
    def get_all_couch_responses(cls):
        ret = []
        for sample_user in cls.sample_users:
            ret.append(sample_user.get_couch_mock())
        for sample_event in cls.sample_events:
            ret.append(sample_event.get_couch_mock())
        return ret

    @classmethod
    def mongo_get_data_side_effect(cls, event_ids=None, user_ids=None):
        # print('called mongo_side_effect with:', {'event_ids': event_ids,
        #                                          'user_ids': user_ids})

        def handle_user(logs, u_ids, e_ids):
            return [entry for entry in logs if entry['userId'] in u_ids]

        def handle_event(logs, u_ids, e_ids):
            return [entry for entry in logs if entry['eventId'] in e_ids]

        def handle_both(logs, u_ids, e_ids):
            return [entry for entry in logs
                    if entry['eventId'] in e_ids and entry['userId'] in u_ids]

        handler = None
        if event_ids and user_ids:
            handler = handle_both
        elif event_ids:
            handler = handle_event
        elif user_ids:
            handler = handle_user

        event_ids, user_ids = make_iterable(evnt_ids=event_ids,
                                            usr_ids=user_ids)

        all_logs = cls.get_all_mongo_logs()
        ret = handler(logs=all_logs, u_ids=user_ids, e_ids=event_ids)
        return ret

    @classmethod
    def couch_get_data_side_effect(cls, event_ids=NOT_CALLED,
                                   user_ids=NOT_CALLED):
        # print('called couch_side_effect with:', {'event_ids': event_ids,
        #                                          'user_ids': user_ids})

        event_ids, user_ids = make_iterable(evnt_ids=event_ids,
                                            usr_ids=user_ids)
        # Default value is None or string from it
        selected_ids = [each for each in event_ids + user_ids
                        if each not in ('None', None)]

        # Check if row is for what we've asked
        ret = [row for row in cls.get_all_couch_responses()
               if row.key in selected_ids]
        return ret


class DbPatcherMixin:
    # TODO: Join timestamp present, leave not, and the other way around
    # TODO: Event start/end time approximation when for ^those^ 4 cases

    # TODO: Split this class for mixins?

    get_expected_users = ResponseFactory.get_users_for_given_event_class

    # Suppress IDE warnings
    patcher_coach_get_data = patcher_coach_init = \
        patcher_mongo_get_data = patcher_mongo_init = \
        mock_coach_get_data = mock_coach_init = \
        mock_mongo_get_data = mock_mongo_init = None

    def setUp(self):
        couch_side_effects = ResponseFactory.couch_get_data_side_effect
        mongo_side_effects = ResponseFactory.mongo_get_data_side_effect

        self.patcher_coach_get_data = patch.object(
            CouchData, 'get_data', side_effect=couch_side_effects)
        self.patcher_coach_init = patch.object(
            CouchData, '__init__', return_value=None)

        self.patcher_mongo_get_data = patch.object(
            MongoData, 'get_data', side_effect=mongo_side_effects)
        self.patcher_mongo_init = patch.object(
            MongoData, '__init__', return_value=None)

        # Start patch
        self.mock_coach_get_data = self.patcher_coach_get_data.start()
        self.mock_coach_init = self.patcher_coach_init.start()

        self.mock_mongo_get_data = self.patcher_mongo_get_data.start()
        self.mock_mongo_init = self.patcher_mongo_init.start()

        # Stop patch
        self.addCleanup(patch.stopall)

        # Reset settings, as there is only one instance of this class
        Setts.refresh(reset=True)

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
        self.assertEqual(len(expected_events_users), len(script_events_users))

        for user in script_events_users:
            # Dunno in which order it was added to sample data
            expected_user = [u for u in expected_events_users
                             if u.userId == user.user_id][0]

            self.assertEqual(expected_user.userId, user.user_id)
            self.assertEqual(expected_user.display_name, user.display_name)
            self.assertEqual(
                expected_user.get_timestamp(event_id=event_id),
                user.timestamp,
                msg='Timestamps mismatch. User was logged earlier!'
            )

    def check_if_participants_in_alphabetical_order(self, ca_events):
        for ca_event in ca_events:
            expected_users = self.get_users_in_alphabetical_order(ca_event)
            actual_users = ca_event.event_participants()
            users = (expected_users, actual_users)

            self.assertEqual(len(expected_users), len(actual_users))

            for expected_usr, actual_usr in zip(*users):
                self.assertEqual(expected_usr.userId, actual_usr.user_id,
                                 msg='Users are not in alphabetical order!')
                self.assertEqual(expected_usr.display_name,
                                 actual_usr.display_name)

    @classmethod
    def get_users_in_alphabetical_order(cls, ca_event):
        ca_event_id = ca_event.event_id
        real_event_participants = (ResponseFactory.
                                   get_all_users_attending_event(ca_event_id))
        sorted_participants = sorted(real_event_participants,
                                     key=lambda x: x.display_name)
        return sorted_participants

    def check_if_participants_in_join_order(self, ca_events):
        # @TODO: Refactor with check_if_participants_in_alphabetical_order
        for ca_event in ca_events:
            expected_users = self.get_users_in_join_order(ca_event)
            actual_users = ca_event.event_participants()
            users = (expected_users, actual_users)

            self.assertEqual(len(expected_users), len(actual_users))

            for expected_usr, actual_usr in zip(*users):
                self.assertEqual(expected_usr.userId, actual_usr.user_id,
                                 msg='Users are not in join order!')
                self.assertEqual(expected_usr.display_name,
                                 actual_usr.display_name)

    @classmethod
    def get_users_in_join_order(cls, ca_event):
        # TODO: Refactor with get_users_in_alphabetical_order
        ca_event_id = ca_event.event_id
        real_event_participants = (ResponseFactory.
                                   get_all_users_attending_event(ca_event_id))
        sorted_participants = sorted(
            real_event_participants,
            key=lambda x: x.get_join_earliest_timestamp(event_id=ca_event_id))
        return sorted_participants

    @classmethod
    def get_events_first_user_timestamp(cls, event_class):
        """
        It takes leave timestamp only for the first user.

        :param event_class:
        :return:
        """
        # We need to get user(s) connected to that event.
        users_connected_with_this_event = (
            ResponseFactory.get_users_for_given_event_class(
                event_list=[event_class]
            ))

        # Response from this function is indexed by the class :]
        user_attending_the_event = (
            users_connected_with_this_event[event_class][0])

        # When we have user we don't need to go to all his logs.
        # There is method getting latest leave time for us
        expected_timestamp = (
            user_attending_the_event.get_timestamp(
                event_id=event_class.eventId
            ))
        return expected_timestamp
