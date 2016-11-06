#!/usr/bin/env python3
# (c) 2016 Alek
#  Engine for ca analytics
import collections
import logging

import dateutil.parser

log = logging.getLogger(__name__)


def get_ca_events(db_data):
    def fill_couchdb_info(ca_events_list):
        for ca_evnt in ca_events_list:
            ca_evnt.fill_with_couch_details()

    # Effective deduplication mechanism
    events = collections.defaultdict(CaEvent)

    for row in db_data:
        eventId = row['eventId']
        events[eventId].append(log_entry=row)

    # Get rid of dict, and sort by id
    ret = sorted(events.values(), key=lambda x: x.event_id)

    fill_couchdb_info(ca_events_list=ret)
    return ret


class CaUser:
    _user_id = None
    _timestamp = None

    _mongo_raw_data = None
    _couch_raw_data = None

    def __init__(self, log_entry):
        """
        {'_id': ObjectId('57a3a39a00c88030ca45cddb'),
          'action': 'join',
          'connectedUsers': 0,
          'eventId': 523,
          'level': 'info',
          'message': 'events',
          'timestamp': '2016-07-02T20:35:40.896Z',
          'userId': '108333970581946079744'}
        :param log_entry:
        """
        self.user_id = log_entry['userId']
        self.timestamp = log_entry['timestamp']

        self._mongo_raw_data = log_entry

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        """ Sets EventId for this class. """
        if self._user_id is None:
            self._user_id = value
        elif self._user_id != value:
            log.error('Tried to change user_id of the class! [%s]->[%s]. '
                      'This should never happen. Statistics may be corrupted.',
                      self._user_id, value)

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        """ '2016-07-02T20:35:40.896Z' """
        value = dateutil.parser.parse(value)

        if self._timestamp is None:
            self._timestamp = value
        elif self._timestamp != value:
            log.error('Tried to change timestamp of the class! [%s]->[%s]. '
                      'This should never happen. Statistics may be corrupted.',
                      self._timestamp, value)

    def __str__(self):
        return 'userId [%s]@[%s]' % (self.user_id, self.timestamp)

    def __repr__(self):
        return 'userId [%s]@[%s]' % (self.user_id, self.timestamp)


class CaEvent:
    _event_id = None
    _user_list = None

    _couch_raw_data = None

    @property
    def event_id(self):
        return self._event_id

    @event_id.setter
    def event_id(self, value):
        """ Sets EventId for this class. """
        if self._event_id is None:
            self._event_id = value
        elif self._event_id != value:
            log.error('Tried to change event_id of the class! [%s]->[%s]. '
                      'This should never happen. Statistics may be corrupted.',
                      self._event_id, value)

    @property
    def user_list(self):
        return self._user_list

    def user_list_append(self, value):
        if self._user_list is None:
            self._user_list = [value]
        else:
            self._user_list.append(value)

    def append(self, log_entry):
        self.event_id = log_entry['eventId']
        ca_user = CaUser(log_entry=log_entry)
        self.user_list_append(ca_user)

    def fill_with_couch_details(self):
        # TODO: Get CouchDB details about event and users
        pass

    def __str__(self):
        return 'eventId [%s] user_list %s' % (self.event_id, self.user_list)
