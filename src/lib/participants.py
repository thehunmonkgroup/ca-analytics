import logging

import dateutil.parser

from lib.database import MongoFields, UserFields
from lib.extras import STRFTIME_FORMAT, Setts

log = logging.getLogger(__name__)


class CaParticipant:
    # Log entries
    _user_id = None
    action = None
    _timestamp = None
    _timestamp_str = None

    # Details
    _display_name = None

    # Storage variables
    _raw_log_entry = None
    _raw_details = None
    _details = None

    # TODO: Proper error handling
    _error_msg_change = (
        'Tried to change [%s] of the user [%s]! [%s]->[%s]. '
        'This should never happen. Statistics may be corrupted.'
    )
    _str_representation_templ = 'User: [%s] - [%s], Joined: [%s]'

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
        self.user_id = log_entry[MongoFields.USER_ID]
        self.action = log_entry[MongoFields.ACTION]

        self._raw_log_entry = log_entry
        self._raw_details = Setts.details_provider[self.user_id]

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
        if self._timestamp is not None:
            return self._timestamp

        raw_value = self._raw_log_entry[MongoFields.TIMESTAMP]
        try:
            self._timestamp = dateutil.parser.parse(raw_value)
        except AttributeError as e:
            log.warning(
                'Error converting [%s] to date object for participant [%s]. '
                'Returning his action [%s] as [%s]. \n %s',
                raw_value, self.user_id, self.action, self._timestamp, e)
        return self._timestamp

    @property
    def timestamp_str(self):
        try:
            return self.timestamp.strftime(STRFTIME_FORMAT)
        except Exception as e:
            log.debug(e)
            return str(self._timestamp)

    @property
    def display_name(self):
        if self._display_name is None:
            self._display_name = self._raw_details[UserFields.DISPLAY_NAME]
        return self._display_name

    def __hash__(self):
        return hash(self.user_id)
        ## Show all users
        # return (hash(self.user_id) ^
        #         hash(self._timestamp_str))

    def __eq__(self, other):
        return other.user_id == self.user_id
        ## Show all users
        # if other.user_id != self.user_id:
        #     return other.user_id < self.user_id
        # elif other.timestamp == self.timestamp:  # All equal!
        #     return other.timestamp == self.timestamp
        # else:  # Same id, compare based on timestampe
        #     return other.timestamp < self.timestamp

    def __gt__(self, other):
        ## Sort by id
        # return other.user_id < self.user_id
        ## Sort by time entered
        return other.timestamp < self.timestamp
        ## Sort by id & time one hopped in
        # if other.user_id == self.user_id:
        #     return other.timestamp < self.timestamp
        # else:
        #     return other.user_id < self.user_id

    def __str__(self):
        data_for_templ = (self.user_id, self.display_name,
                          self.timestamp_str)
        return self._str_representation_templ % data_for_templ

    def __repr__(self):
        return 'userId [%s]@[%s]' % (self.user_id, self.timestamp_str)


class CaUserOld:
    display_name = None

    _user_id = None
    _timestamp = None
    _timestamp_str = None

    _mongo_raw_data = None
    _couch_raw_data = None

    # TODO: Proper error handling
    _error_msg_change = (
        'Tried to change [%s] of the user [%s]! [%s]->[%s]. '
        'This should never happen. Statistics may be corrupted.'
    )
    _str_representation_templ = 'User: [%s] - [%s], Joined: [%s]'

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
        log.warning('Usr [%s] - setting missing (TODO)', self.user_id)
        # TODO: Set missing for CouchDB (this should not happen often)

    def __hash__(self):
        return hash(self.user_id)
        ## Show all users
        # return (hash(self.user_id) ^
        #         hash(self._timestamp_str))

    def __eq__(self, other):
        return other.user_id == self.user_id
        ## Show all users
        # if other.user_id != self.user_id:
        #     return other.user_id < self.user_id
        # elif other.timestamp == self.timestamp:  # All equal!
        #     return other.timestamp == self.timestamp
        # else:  # Same id, compare based on timestampe
        #     return other.timestamp < self.timestamp

    def __gt__(self, other):
        ## Sort by id
        # return other.user_id < self.user_id
        ## Sort by time entered
        return other.timestamp < self.timestamp
        ## Sort by id & time one hopped in
        # if other.user_id == self.user_id:
        #     return other.timestamp < self.timestamp
        # else:
        #     return other.user_id < self.user_id

    def __str__(self):
        data_for_templ = (self.user_id, self.display_name,
                          self.timestamp.strftime(STRFTIME_FORMAT))
        return self._str_representation_templ % data_for_templ

    def __repr__(self):
        return 'userId [%s]@[%s]' % (self.user_id, self.timestamp)


class ParticipantsHandler:
    """
    Important handler class for users attending the event.
    Knows about all users from this event.

    If you want to get all users from particular event, you must change hash
      algorithm of the CaUser class, so that set() won't throw it out.
    """
    _participant_list = None

    def __init__(self):
        self._participant_list = []

    @property
    def unique(self):
        """
        Return deduplicated users with earliest time they joined an event and
         sorted id ascending.

        :return:
        """
        if self._participant_list is None:
            log.warning('Accessing uninitialized user list')
            return []
        else:
            # Earliest date is returned, cos the first object in set is
            # retained.
            # As it happens with logs-earliest date comes first. And this is
            # the object that is retained in set. The rest (later mentions of
            # user connecting to the event) is disposed. Can we relay on it?
            return sorted(set(self._participant_list))

    @property
    def unique_ids(self):
        ids = (x.user_id for x in self.unique)
        return sorted(set(ids))

    def add(self, log_entry):
        ca_participant = CaParticipant(log_entry=log_entry)
        self._participant_list.append(ca_participant)
