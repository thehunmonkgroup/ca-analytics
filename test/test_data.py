#!/usr/bin/env python3
# (c) 2016 Alek
#  Test data for Circle Anywhere

import logging
import os
import sys
from abc import ABCMeta

from unittest.mock import MagicMock

rwd = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
if rwd not in sys.path:
    sys.path.append(rwd)

log = logging.getLogger(__name__)


def get_mongo_row_mock(id, key, value):
    mock_mongo_response = MagicMock(spec=['id', 'key', 'value'],
                                    name='Row')
    mock_mongo_response.id = id
    mock_mongo_response.key = key
    mock_mongo_response.value = value
    return mock_mongo_response


def get_event_name(evnt_id):
    return 'event/%s' % str(evnt_id).ljust(5, '0')


class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class BaseEventMock(metaclass=ABCMeta):
    eventId = None
    dateAndTime = None
    _resp_value = None

    @classmethod
    def get_mongo_mock(cls):
        return get_mongo_row_mock(id=cls.get_mongo_id(), key=cls.eventId,
                                  value=cls.resp_value)

    @ClassProperty
    @classmethod
    def resp_value(cls):
        ret = cls._resp_value.copy()
        ret['id'] = str(cls.eventId)
        ret['_id'] = cls.get_mongo_id()
        ret['dateAndTime'] = cls.dateAndTime
        return ret

    @classmethod
    def get_mongo_id(cls):
        return get_event_name(evnt_id=cls.eventId)


class Event111(BaseEventMock):
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


class Event222(BaseEventMock):
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


class BaseUserMock(metaclass=ABCMeta):
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

    _mongo_value = None

    @classmethod
    def get_mongo_mock(cls):
        return get_mongo_row_mock(id=cls.mongo_id, key=cls.userId,
                                  value=cls.mongo_value)

    @ClassProperty
    @classmethod
    def mongo_value(cls):
        ret = cls._mongo_value.copy()
        ret['id'] = str(cls.userId)
        ret['_id'] = cls.mongo_id
        ret['displayName'] = '%s %s' % (cls.givenName, cls.familyName)
        name = {'familyName': cls.familyName,
                'givenName': cls.givenName}
        ret['name'] = name
        ret['emails'] = cls.emails
        ret['google_json'] = cls.google_json
        return ret

    @ClassProperty
    @classmethod
    def mongo_id(cls):
        return 'user/%s' % cls.userId


class User111(BaseUserMock):
    userId = 102137774477271133111
    givenName = 'John'
    familyName = 'Doe'
    emails = [{'value': 'fake_john_doe@gmail.com'}]

    _mongo_value = {
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
