import logging
import operator
from collections import defaultdict

import dateutil.parser

from lib.database import MongoFields, UserFields
from lib.extras import STRFTIME_FORMAT, Setts

log = logging.getLogger(__name__)


class ParticipantsHandler:
    """
    Important handler class for users attending the event.
    Knows about all users from this event.

    If you want to get all users from particular event, you must change hash
      algorithm of the CaUser class, so that set() won't throw it out.
    """
    _participant_list = None
    _participant_dict = None

    def __init__(self):
        self._participant_list = []
        self._participant_dict = defaultdict(CaParticipant)

    @property
    def unique(self):
        sorting_key = Setts.ORDER_BY.participant_sort_keys

        all_sorted = self.get_all_sorted(sort_key=sorting_key)

        # Dispose of all redundant participant logs, but leave first occurance
        return sorted(set(all_sorted), key=sorting_key)

    @property
    def unique_ids(self):
        ids = (x.user_id for x in self.unique)
        return sorted(set(ids))

    def get_join_timestamps(self, join_sort_key=None):
        """
        Return join timestamps in descending order, unless join_sort_key will
          sort it differently.

        :param join_sort_key:
        :return:
        """
        join_sort_key = (join_sort_key or
                         operator.attrgetter(Setts._OrderByOpt.OUR_JOIN_TIME))

        participant_join_timestamps = tuple(
            participant.timestamp for participant
            in self.get_all_sorted(sort_key=join_sort_key))

        return participant_join_timestamps

    def get_all_sorted(self, sort_key=Setts.ORDER_BY.participant_sort_keys):
        """
        Return deduplicated users with earliest time they joined an event and
         sorted id ascending.

        :return:
        """
        if self._participant_list is None:
            log.warning('Accessing uninitialized user list')
            return []
        else:
            # Sort two times. First so that set() will memorize first correct
            #   object. Second cos set() is not preserving order.
            all_sorted = sorted(self._participant_list, key=sort_key)
            return all_sorted

    def add(self, log_entry):
        participant_id = log_entry['userId']
        self._participant_dict[participant_id].add(log_entry)

        ca_participant = CaParticipantLogEntry(log_entry=log_entry)
        self._participant_list.append(ca_participant)


class CaParticipant:
    _user_id = None

    _action_join_list = None
    _action_leave_list = None

    _ACTION_JOIN = 'join'
    _ACTION_LEAVE = 'leave'

    _str_templ = 'User [%s] jumped in [%s]/[%s] out times from event [%s]'
    _error_msg_change = (
        'Tried to change [%s] of the user [%s]! [%s]->[%s]. '
        'This should never happen. Statistics may be corrupted.'
    )

    def __init__(self):
        """
        This class stores users all actions, join/leave.
        Supported actions: 'join' | 'leave'
        """
        # Be careful if you want to change it to dict - hashing of
        #   `CaParticipantLogEntry` may remove entries from dict.
        self._action_join_list = []
        self._action_leave_list = []

    @property
    def user_id(self):
        """ It'e here cos we want to check if log is for correct user. """
        return self._user_id

    @property
    def event_id(self):
        """ Pick `event_id` from first parsed log entry. """
        # Maybe one or the other is empty
        users_to_check = self._action_join_list or self._action_leave_list
        return users_to_check[0].event_id

    @user_id.setter
    def user_id(self, value):
        """ Sets EventId for this class. """
        value = int(value)
        if self._user_id is None:
            self._user_id = value
        elif self._user_id != value:
            log.error(self._error_msg_change,
                      MongoFields.USER_ID, self.user_id, self._user_id, value)

    def add(self, log_entry):
        self.user_id = log_entry[MongoFields.USER_ID]

        ca_participant = CaParticipantLogEntry(log_entry=log_entry)
        if ca_participant.action == self._ACTION_JOIN:
            self._action_join_list.append(ca_participant)
        elif ca_participant.action == self._ACTION_LEAVE:
            self._action_leave_list.append(ca_participant)
        else:
            raise RuntimeError(
                'Unrecognized action [{}] for log_entry [{}]'.format(
                    ca_participant.action, log_entry))

    def __str__(self):
        data_for_templ = (self.user_id, len(self._action_join_list),
                          len(self._action_leave_list), self.event_id)
        return self._str_templ % data_for_templ

    __repr__ = __str__


class CaParticipantLogEntry:
    # Log entries
    _user_id = None
    _event_id = None
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
        self.event_id = log_entry[MongoFields.EVENT_ID]
        self.action = log_entry[MongoFields.ACTION]

        self._raw_log_entry = log_entry
        self._raw_details = Setts.details_provider[self.user_id]

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        """ Sets EventId for this class. """
        # TODO: Here validation is probably not needed as one instance of
        #       the class corresponds to one log_entry
        value = int(value)
        if self._user_id is None:
            self._user_id = value
        elif self._user_id != value:
            log.error(self._error_msg_change,
                      MongoFields.USER_ID, self.user_id, self._user_id, value)

    @property
    def event_id(self):
        """ It'e here cos we want to check if log is for correct user. """
        return self._event_id

    @event_id.setter
    def event_id(self, value):
        """ Sets EventId for this class. """
        value = int(value)
        if self._event_id is None:
            self._event_id = value
        elif self._event_id != value:
            log.error(self._error_msg_change,
                      'event_id', self.user_id, self._event_id, value)

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
        return 'user [%s]@[%s] name [%s]' % (self.user_id, self.timestamp_str,
                                             self.display_name)
