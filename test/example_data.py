#!/usr/bin/env python3
# (c) 2016 Alek
#  Test data for Circle Anywhere

import logging
import os
import sys
from abc import ABCMeta
from collections import namedtuple
from unittest.mock import MagicMock

import dateutil

from lib.extras import make_iterable

rwd = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
if rwd not in sys.path:
    sys.path.append(rwd)

log = logging.getLogger(__name__)


def get_couch_row_mock(id, key, value):
    mock_couch_response = MagicMock(spec=['id', 'key', 'value'],
                                    name='Row')
    mock_couch_response.id = id
    mock_couch_response.key = key
    mock_couch_response.value = value
    mock_couch_response.value = value

    return mock_couch_response


class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


MongoLogSetup = namedtuple('mongo_log_setup', ['event_id',
                                               'timestamps_from_earliest'])


class ObjectId:
    """ Dummy for MongoDB data. """

    def __init__(self, foo):
        self.foo = foo

    def __repr__(self):
        return "ObjectId('%s')" % self.foo


class BaseCouchEventMock(metaclass=ABCMeta):
    eventId = None
    dateAndTime = None
    _resp_value = None

    @classmethod
    def get_couch_mock(cls):
        return get_couch_row_mock(id=cls.couch_id_name, key=cls.eventId,
                                  value=cls.couch_value_response)

    @ClassProperty
    @classmethod
    def couch_value_response(cls):
        ret = cls._resp_value.copy()
        ret['id'] = str(cls.eventId)
        ret['_id'] = cls.couch_id_name
        ret['dateAndTime'] = cls.dateAndTime
        return ret

    @ClassProperty
    @classmethod
    def description(cls):
        ret = cls._resp_value['description']
        return ret

    @ClassProperty
    @classmethod
    def calendar_id(cls):
        ret = cls._resp_value['calendarId']
        return ret

    @ClassProperty
    @classmethod
    def start_time(cls):
        ret = dateutil.parser.parse(cls.dateAndTime)
        return ret

    @ClassProperty
    @classmethod
    def couch_id_name(cls):
        return 'event/%s' % str(cls.eventId).ljust(5, '0')


class BaseCouchUserMock(metaclass=ABCMeta):
    userId = None
    givenName = None
    familyName = None
    emails = None
    google_json = {
        'verified_email': True,
        'given_name': 'Fake',
        'picture': 'https://lh4.googleusercontent.com/-yI/photo.jpg',
        'email': 'fake@example.com',
        'family_name': 'Fake',
        'gender': 'male',
        'link': 'https://plus.google.com/+Fake',
        'id': '102144444444444444444',
        'locale': 'de',
        'name': 'Fake Fake',
    }

    _couch_value = None

    @classmethod
    def get_couch_mock(cls):
        return get_couch_row_mock(id=cls.couch_id_name, key=cls.userId,
                                  value=cls.couch_value_response)

    @ClassProperty
    @classmethod
    def couch_value_response(cls):
        ret = cls._couch_value.copy()
        ret['id'] = str(cls.userId)
        ret['_id'] = cls.couch_id_name
        ret['displayName'] = cls.display_name
        name = {'familyName': cls.familyName,
                'givenName': cls.givenName}
        ret['name'] = name
        ret['emails'] = cls.emails
        ret['google_json'] = cls.google_json
        return ret

    @ClassProperty
    @classmethod
    def display_name(cls):
        return '%s %s' % (cls.givenName, cls.familyName)

    @ClassProperty
    @classmethod
    def couch_id_name(cls):
        return 'user/%s' % cls.userId


class BaseMongoUserMock(metaclass=ABCMeta):
    userId = None
    # Timestamps must be in ascending order
    _participated_in = []

    _LOG_TEMPLATE = {
        '_id': None,
        'action': 'join',
        'connectedUsers': 0,
        'eventId': None,
        'level': 'info',
        'message': 'events',
        'timestamp': None,
        'userId': None
    }

    @classmethod
    def get_mongo_response(cls):

        def get_logs_for_this_event(event_id, timestamps_list):
            ret_ = []
            for timestamp in timestamps_list:
                entry = cls._get_log_entry(eventId=event_id,
                                           timestamp=timestamp)
                ret.append(entry)
            return ret_

        ret = []
        for log_setup in cls._participated_in:
            log_entries = get_logs_for_this_event(
                event_id=log_setup.event_id,
                timestamps_list=log_setup.timestamps_from_earliest
            )
            ret.extend(log_entries)
        return ret

    @classmethod
    def get_earliest_timestamp(cls, event_id):
        # dateutil.parser.parse
        event = [e for e in cls._participated_in if e.event_id == event_id][0]
        earliest_timestamp = event.timestamps_from_earliest[0]
        # earliest_timestamp = '2016-05-12T17:51:24.633Z'
        return dateutil.parser.parse(earliest_timestamp)

    @classmethod
    def _get_log_entry(cls, eventId, timestamp):
        ret = cls._LOG_TEMPLATE.copy()
        # TODO: Generate it
        ret['_id'] = ObjectId('57a3a39800c88030ca42d248')
        ret['userId'] = cls.userId
        ret['eventId'] = eventId
        ret['timestamp'] = timestamp
        return ret


class Event111(BaseCouchEventMock):
    eventId = 111
    dateAndTime = '2016-05-12T19:00:00+00:00'

    _resp_value = {
        'timeZoneValue': 'America/Chicago',
        'duration': 60,
        'adminProposedSessions': True,
        'shortName': None,
        'whiteboard': {
            'message': "Welcome everyone! Please let us know if you can't hear or see us by using the chat box below. Only two video feeds are available at once, so you can't be seen unless we pull your feed up.\nYou can mute or unmute yourself by clicking the microphone on the top left of the video screen. We also have control of muting and unmuting people. Please mute yourself when you're not speaking so there is no background noise. The hand icon next to the mic is for asking a question or getting our attention. We'll wait until everyone is here and then launch in. Thank you for joining us for today's session!"},
        'facilitatorLead': '115823879444446656545',
        'facilitatorCo': '116778744444444444472',
        'description': "Come and discover in the moment what's the most alive in our connection",
        'youtubeEmbed': None,
        'overflowMessage': '',
        'history': {
            'event': {
                '100143114444444444634': {'total': 3214444, 'start': None},
                '110064534444444444409': {'total': 3814444, 'start': None},
                '113346384444444444429': {'total': 3784444, 'start': None},
                '101920114444444444407': {'total': 3634444, 'start': None},
                '115823874444444444445': {'total': 3854444, 'start': None},
                '106432114444444444429': {'total': 3554444, 'start': None},
                '116778744444444444472': {'total': 3854444, 'start': None},
                '113831464444444444449': {'total': 3624444, 'start': None}},
            'sessions': {
                '940': {'115823879444444444444': {'total': 26, 'start': None},
                        '100143115744444444444': {'total': 6, 'start': None},
                        '110064536344444444444': {'total': 10, 'start': None},
                        '113346387144444444444': {'total': 13, 'start': None},
                        '116778749344444444444': {'total': 17, 'start': None},
                        '101920115444444444444': {'total': 19, 'start': None},
                        '106432116644444444444': {'total': 4, 'start': None},
                        '113831464244444444444': {'total': 11,
                                                  'start': None}}}},
        'calendarId': 'member',
        'previousVideoEmbeds': [],
        '_rev': '261-8090b269e44444aedf5c18668dff89fa',
        'conferenceOverride': '',
        'dateAndTime': None,
        'sessionProvider': 'google',
        'admins': [
            {'id': '115823844444444444445'}],
        'open': False,
        'title': 'Circling',
        'organizer': 'none',
        'sessionsOpen': True,
        'overflowUserCap': 20,
        'id': None,
        '_id': None,
        'muteLock': False
    }


class Event222(BaseCouchEventMock):
    eventId = 222
    dateAndTime = '2016-07-02T17:00:00+00:00'

    _resp_value = {
        'timeZoneValue': 'Pacific/Honolulu',
        'muteLock': False,
        'duration': 60,
        'adminProposedSessions': True,
        'shortName': None,
        'facilitatorLead': '113444444444444444443',
        'facilitatorCo': '102137444444444444448',
        'description': 'Whats alive in you NOW?',
        'youtubeEmbed': None,
        'overflowMessage': '',
        'history': {
            'event': {
                '113445444444444444444': {'total': 3984444, 'start': None},
                '108333444444444444444': {'total': 4224444, 'start': None},
                '100958444444444444444': {'total': 4334444, 'start': None},
                '113346444444444444444': {'total': 1034444, 'start': None},
                '104470444444444444444': {'total': 4334444, 'start': None},
                '102137444444444444444': {'total': 4334444, 'start': None},
                '100143444444444444444': {'total': 4314444, 'start': None},
                '116228444444444444444': {'total': 4334444, 'start': None},
                '106432444444444444444': {'total': 4284444, 'start': None},
                '108611444444444444444': {'total': 4334444, 'start': None},
                '107452444444444444444': {'total': 3634444, 'start': None}},
            'sessions': {
                '1165': {'108333970581444444444': {'total': 11, 'start': None},
                         '108611793445444444444': {'total': 7, 'start': None},
                         '107452622478444444444': {'total': 1, 'start': None},
                         '102137775077444444444': {'total': 2, 'start': None},
                         '100143115762444444444': {'total': 5, 'start': None}},
                '1164': {
                    '113445281444444444444': {'total': 1334300, 'start': None},
                    '108333971444444444444': {'total': 5, 'start': None},
                    '102137771444444444444': {'total': 3, 'start': None},
                    '104470311444444444444': {'total': 14, 'start': None},
                    '100958091444444444444': {'total': 13, 'start': None},
                    '100143111444444444444': {'total': 6, 'start': None},
                    '116228711444444444444': {'total': 31, 'start': None},
                    '106432111444444444444': {'total': 16, 'start': None},
                    '108611791444444444444': {'total': 9, 'start': None}}}},
        'calendarId': 'member',
        'previousVideoEmbeds': [],
        '_rev': '379-e7ece17fd61440dc09ba79228bad6326',
        'conferenceOverride': '',
        'dateAndTime': None,
        'sessionProvider': 'google',
        'admins': [{'id': '113445282444444444443'},
                   {'id': '102137775444444444448'}],
        'open': False,
        'title': 'Circling', 'whiteboard': {
            'message': "Welcome everyone! Please let us know if you can't hear or see us by using the chat box below. Only two video feeds are available at once, so you can't be seen unless we pull your feed up.\n\nYou can mute or unmute yourself by clicking the microphone on the top left of the video screen. We also have control of muting and unmuting people. Please mute yourself when you're not speaking so there is no background noise. We'll wait until everyone is here and then launch in. Thank you for joining us for today's session!"},
        'sessionsOpen': True,
        'overflowUserCap': 20,
        'id': None,
        '_id': None,
        'organizer': 'none'
    }


class User111(BaseCouchUserMock, BaseMongoUserMock):
    userId = 102137774477271133111
    givenName = 'John'
    familyName = 'Doe'
    emails = [{'value': 'fake_john_doe@gmail.com'}]

    _couch_value = {
        'perms': {'joinEvents': False,
                  'createEvents': True},
        'picture': 'https://lh4.googleusercontent.com/-yI/photo.jpg',
        'link': 'https://plus.google.com/+Buba',
        '_rev': '96-7b43ab17f2c85079aee44d8a044c2a5b',
        'provider': 'google',
        'isPlusUser': True,
        'admin': False,
        'displayName': None,
        '_id': None,
        'name': None,
        'preferredContact': {},
        'emails': None,
        'superuser': False,
        'createdViaHangout': False,
        'id': None,
        'networkList': {'65': ['114346453544444444444'],
                        '240': ['108743734444444444446'],
                        '86': ['100597781244444444444']},
        'google_json': None
    }

    _participated_in = [
        MongoLogSetup(event_id=Event111.eventId,
                      timestamps_from_earliest=[
                          '2016-05-12T16:53:36.363Z',
                          '2016-05-12T17:48:03.286Z',
                          '2016-05-12T17:50:35.528Z',
                          '2016-05-12T19:00:11.024Z',
                          '2016-05-12T19:01:16.784Z',
                      ]),
        MongoLogSetup(event_id=Event222.eventId,
                      timestamps_from_earliest=[
                          '2016-07-02T16:59:56.186Z',
                          '2016-07-02T16:59:58.835Z',
                          '2016-07-02T17:00:21.574Z',
                          '2016-07-02T18:02:34.475Z',
                      ]),
    ]


class User222(BaseCouchUserMock, BaseMongoUserMock):
    userId = 107452622478341478222
    givenName = 'Luís'
    familyName = 'Bäcker '
    emails = [{'value': 'luis_backer@example.com'}]

    _couch_value = {
        'perms': {'joinEvents': False},
        'picture': 'https://lh3.googleusercontent.com/-X5M/photo.jpg',
        'link': 'https://plus.google.com/107',
        '_rev': '74-47ce5c69e1c3eebb3e9e58f444060bea',
        'provider': 'google',
        'isPlusUser': True,
        'admin': False,
        'displayName': None,
        '_id': None,
        'name': None,
        'preferredContact': {},
        'emails': None,
        'superuser': False,
        'createdViaHangout': False,
        'id': None,
        'networkList': {},
        'google_json': None
    }

    _participated_in = [
        MongoLogSetup(event_id=Event111.eventId,
                      timestamps_from_earliest=[
                          '2016-05-12T14:46:04.450Z',
                          '2016-05-12T17:51:24.633Z',
                          '2016-05-12T19:01:01.030Z',
                          '2016-05-12T20:15:17.536Z',
                      ]),
    ]


class ResponseFactory:
    NOT_CALLED = 'not called'
    sample_users = [
        User111,
        User222
    ]
    sample_events = [
        Event111,
        Event222
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
    def mongo_get_data_side_effect(cls, event_ids=NOT_CALLED,
                                   user_ids=NOT_CALLED):
        # print('called mongo_side_effect with:', {'event_ids': event_ids,
        #                                          'user_ids': user_ids})

        event_ids, user_ids = make_iterable(evnt_ids=event_ids,
                                            usr_ids=user_ids)
        ret = [entry for entry in cls.get_all_mongo_logs()
               if entry['eventId'] in event_ids or entry['userId'] in user_ids]
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
