#!/usr/bin/env python3
# (c) 2016 Alek
#  Engine for ca analytics
import collections
import logging

import dateutil.parser
import dateutil.relativedelta

from lib.extras import Setts

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

    # From Couch db
    description = None
    calendar_id = None
    _start_time = None
    _end_time = None
    duration = None

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
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, value):
        """ Sets EventId for this class. """
        value = dateutil.parser.parse(value)
        if self._start_time is None:
            self._start_time = value
        elif self._start_time != value:
            log.error('Tried to change _start_time of the class! [%s]->[%s]. '
                      'This should never happen. Statistics may be corrupted.',
                      self._start_time, value)

    @property
    def end_time(self):
        if self._end_time is not None:
            return self._end_time

        try:
            dt = dateutil.relativedelta.relativedelta(minutes=self.duration)
        except TypeError as e:
            log.debug(e)
            dt = dateutil.relativedelta.relativedelta(minutes=0)

        self._end_time = self._start_time + dt
        return self._end_time

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
        def extend_event_data():
            for row in self._couch_raw_data:
                if row.id.startswith('event/'):
                    self.description = row.value['description']
                    self.calendar_id = row.value['calendarId']
                    self.start_time = row.value['dateAndTime']
                    self.duration = row.value['duration']

        couch_get_data = Setts._DB_COUCH.value.get_data
        self._couch_raw_data = couch_get_data(event_ids=self.event_id)
        extend_event_data()

        # TODO: Get CouchDB details about users

    def __str__(self):
        txt = 'eventId [%s] users_count [%s] time [%s]-[%s] description [%s]'
        return txt % (self.event_id, len(self.user_list),
                      self.start_time, self.end_time, self.description)
