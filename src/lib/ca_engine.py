#!/usr/bin/env python3
# (c) 2016 Alek
#  Engine for ca analytics
import collections
import logging

import dateutil.parser
import dateutil.relativedelta

from lib.extras import Setts, COUCH_DB_MISSING_DATA

log = logging.getLogger(__name__)


def get_ca_events(db_data):
    """
    Return [CaEvent(), CaEvent(), ...]

    :param db_data:
    :return:
    """

    def fill_couchdb_info(ca_events_list):
        for ca_evnt in ca_events_list:
            ca_evnt.fill_with_couch_details()

    # Effective deduplication mechanism
    events = collections.defaultdict(CaEvent)

    for row in db_data:
        # print('processing:', row)
        eventId = row['eventId']
        events[eventId].append(log_entry=row)

    # Get rid of dict, and sort by id
    ret = sorted(events.values(), key=lambda x: x.event_id)

    fill_couchdb_info(ca_events_list=ret)
    return ret


class CaUser:
    display_name = None

    _user_id = None
    _timestamp = None
    _timestamp_str = None

    _mongo_raw_data = None
    _couch_raw_data = None

    # TODO: Proper error handling
    _error_msg_change = ('Tried to change [%s] of the user [%s]! [%s]->[%s]. '
                         'This should never happen. Statistics may be corrupted.')

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
        value = int(value)
        if self._user_id is None:
            self._user_id = value
        elif self._user_id != value:
            log.error(self._error_msg_change,
                      'user_id', self.user_id, self._user_id, value)

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        """ '2016-07-02T20:35:40.896Z' """
        self._timestamp_str = str(value)
        value = dateutil.parser.parse(value)

        if self._timestamp is None:
            self._timestamp = value
        elif self._timestamp != value:
            log.error(self._error_msg_change,
                      'timestamp', self.user_id, self._timestamp, value)

    @property
    def couch_data(self):
        # TODO: check if it can be copied
        if self._couch_raw_data is not None:
            return self._couch_raw_data.copy()
        else:
            return self._couch_raw_data

    @couch_data.setter
    def couch_data(self, value):
        """
           {'perms': {'joinEvents': True},
           'name': {'givenName': 'V', 'familyName': 'Bnt'},
           'displayName': 'V Bt',
           'preferredContact': {},
           'admin': False,
           'id': '1001433634',
           'link': 'https://plus.62434483634',
           'networkList': {'391': ['1165647'],
                           '417': ['10692356718'],
                           '471': ['116485647'],
                           '427': ['11034']},
           'google_json': {'locale': 'en',
                           'name': 'Vnt',
                           'gender': 'female',
                           'given_name': 'V',
                           'email': 'v@gmail.com',
                           'family_name': 'B',
                           'picture': 'https://lh5.content.com/-KJAEs/kE/photo.jpg',
                           'id': '10034',
                           'link': 'https://plus.google.com/1034',
                           'verified_email': True},
           'isPlusUser': True,
           '_rev': '60-3f9676bd925d1d5e35d7cbec75da8d90',
           'picture': 'https://content.com/-KJkE/photo.jpg',
           'superuser': False,
           '_id': 'user/1034',
           'provider': 'google',
           'createdViaHangout': False,
           'emails': [{'value': 'vt@gmail.com'}]}
        """
        self._couch_raw_data = value
        self.display_name = value['displayName']

    def set_missing(self):
        log.debug('Usr [%s] - setting missing', self.user_id)
        # TODO: Set missing for CouchDB (this should not happen often)

    def __hash__(self):
        # return (hash(self.user_id) ^
        #         hash(self._timestamp_str))
        return hash(self.user_id)

    def __eq__(self, other):
        return other.user_id == self.user_id
        # TODO: Test!
        # if other.user_id != self.user_id:
        #     return other.user_id < self.user_id
        # elif other.timestamp == self.timestamp:  # All equal!
        #     return other.timestamp == self.timestamp
        # else:  # Same id, compare based on timestampe
        #     return other.timestamp < self.timestamp

    def __gt__(self, other):
        return other.user_id < self.user_id

    def __str__(self):
        return 'userId [%s]@[%s]' % (self.user_id, self.timestamp)

    def __repr__(self):
        return 'userId [%s]@[%s]' % (self.user_id, self.timestamp)


class EventUsers:
    _users_list = None

    @property
    def unique(self):
        """
        Return deduplicated users with earliest time they joined an event and
         sorted id ascending.

        :return:
        """
        # TODO: earliest time they joined an event
        if self._users_list is None:
            log.warning('Accessing uninitialized user list')
            return []
        else:
            return sorted(set(self._users_list))

    @property
    def unique_ids(self):
        ids = (x.user_id for x in self.unique)
        return sorted(set(ids))

    def get_all_with_earliest_join_time(self):
        pass

    def add(self, log_entry):
        ca_user = CaUser(log_entry=log_entry)

        if self._users_list is None:
            self._users_list = [ca_user]
        else:
            self._users_list.append(ca_user)


class CaEvent:
    _event_id = None
    _event_users = None

    # From Couch db
    description = None
    calendar_id = None
    _start_time = None
    _end_time = None
    duration = None

    _couch_raw_data = None
    _couch_data = None  # Converted to dict

    # TODO: Proper error handling
    _error_msg_change = ('Tried to change [%s] of the event [%s]! [%s]->[%s]. '
                         'This should never happen. Statistics may be corrupted.')

    def __init__(self):
        self._event_users = EventUsers()

    @property
    def event_id(self):
        return self._event_id

    @event_id.setter
    def event_id(self, value):
        """ Sets EventId for this class. """
        value = int(value)
        if self._event_id is None:
            self._event_id = value
        elif self._event_id != value:
            log.error(self._error_msg_change,
                      'event_id', self.event_id, self._event_id, value)

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, value):
        """ Sets EventId for this class. """
        try:
            value = dateutil.parser.parse(value)
        except AttributeError as e:
            # TODO: add stack
            log.debug(e)
            self._start_time = COUCH_DB_MISSING_DATA
            self._end_time = COUCH_DB_MISSING_DATA
            return
        if self._start_time is None:
            self._start_time = value
        elif self._start_time != value:
            log.error(self._error_msg_change,
                      'start_time', self.event_id, self._start_time, value)

    @property
    def couch_data(self):
        return self._couch_data.copy()

    @couch_data.setter
    def couch_data(self, value):
        if self._couch_data is None:
            self._couch_data = value
        elif self._couch_data != value:
            log.error(self._error_msg_change,
                      'couch_data', self.event_id, self._couch_data, value)

    @property
    def end_time(self):
        if self._end_time is not None:
            return self._end_time

        try:
            dt = dateutil.relativedelta.relativedelta(minutes=self.duration)
        except TypeError as e:
            log.error('Error converting duration [%s]. [%s]', self.duration, e)
            dt = dateutil.relativedelta.relativedelta(minutes=0)

        try:
            self._end_time = self._start_time + dt
        except TypeError as e:
            # Probably missing entry of this event in CouchDB
            log.error('Error estimating end time of the event [%s]. '
                      'Start time: %s. Error: %s',
                      self.event_id, self.start_time, e)
        return self._end_time

    @property
    def event_users(self):
        return self._event_users.unique

    # @property
    # def event_users_id(self):
    #     return self._event_users.unique_ids

    # @property
    # def users_id_list(self):
    #     return [usr.user_id for usr in self._event_users]

    def append(self, log_entry):
        self.event_id = log_entry['eventId']
        self._event_users.add(log_entry=log_entry)

    def fill_with_couch_details(self):
        """
        This method should be run when all the data of user_id under this event
         is filled.
        :return:
        """

        def update_event_data(row):
            event_data = {'description': row.value['description'],
                          'calendar_id': row.value['calendarId'],
                          'start_time': row.value['dateAndTime'],
                          'duration': row.value['duration']}

            log.debug('Updating event [%s] with row: %s', self.event_id, row)

            self.description = event_data['description']
            self.calendar_id = event_data['calendar_id']
            self.start_time = event_data['start_time']
            self.duration = event_data['duration']

        def update_child_user_data(child_user, row):
            log.debug('Updating user [%s] with [%s]', child_user, row)
            child_user.couch_data = row.value

        def assign_data():
            """
            Update this event details and all child users of this event with
             CoachDB data.

            _couch_data: {row.id: row}
            row.id, just number

            :return:
            """

            def this_event():
                try:
                    update_event_data(
                        row=self.couch_data.get(self.event_id)
                    )
                except AttributeError as e:
                    log.error("Event [%s] wasn't found in CouchDB. "
                              "Got keys [%s]. Setting fields as missing. "
                              "Error: [%s]",
                              self.event_id, self.couch_data.keys(), e)
                    # TODO: debug, print stack
                    self.set_missing()

            def child_users():
                log.debug('Updating info from CoachDB for users: %s',
                          self.event_users)
                for usr in self.event_users:
                    try:
                        row = self._couch_data[usr.user_id]
                        update_child_user_data(child_user=usr, row=row)
                    except KeyError:
                        log.error("User [%s] wasn't found in CouchDB. "
                                  "Setting user missing. %s", usr.user_id,
                                  self._couch_data)
                        usr.set_missing()

            this_event()
            child_users()

        self._update_with_couch_db_data()

        assign_data()

    def _update_with_couch_db_data(self):
        """
        Get CouchDB data and set it in model.

        :return:
        """
        users_id_list = self._event_users.unique_ids
        couch_data = self.get_couch_data(event_ids=self.event_id,
                                         user_ids=users_id_list)
        self._couch_raw_data = tuple(couch_data)
        # For ease & convenience
        self.couch_data = {int(row.value.get('id', '-1')): row
                           for row in self._couch_raw_data}

    def set_missing(self):
        self.description = COUCH_DB_MISSING_DATA
        self.calendar_id = COUCH_DB_MISSING_DATA
        self._start_time = COUCH_DB_MISSING_DATA
        self._end_time = COUCH_DB_MISSING_DATA
        self.duration = COUCH_DB_MISSING_DATA

    @staticmethod
    def get_couch_data(event_ids=None, user_ids=None):
        return Setts._DB_COUCH.value.get_data(event_ids=event_ids,
                                              user_ids=user_ids)

    def __str__(self):
        txt = 'eventId [%s] users_count [%s] time [%s]-[%s] description [%s]'
        return txt % (self.event_id, len(self.event_users),
                      self.start_time, self.end_time, self.description)
