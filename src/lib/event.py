import dateutil.parser
import dateutil.relativedelta
import logging

from lib.database.engine import MongoFields
from lib.extras import (
    Setts,
    COUCH_DB_MISSING_DATA,
    COUCH_DB_MISSING_TIME,
    STRFTIME_FORMAT,
)
from lib.user import EventUsers

log = logging.getLogger(__name__)


class CaEvent:
    _event_id = None
    _event_users = None

    # From Couch db
    description = None
    calendar_id = None
    _start_time = None
    _end_time = None
    duration = None

    _couch_raw_db_data = None
    _couch_data = None  # Converted to dict

    # TODO: Proper error handling
    _error_msg_change = (
        'Tried to change [%s] of the event [%s]! [%s]->[%s]. '
        'This should never happen. Statistics may be corrupted.'
    )
    _str_representation_templ = (
        '** Event [{event_id}] - [{description}], CalendarId: [{calendar_id}],'
        ' Start/End Time: [{start_time}]/[{end_time}]'
    )

    def __init__(self, event_id):
        self.event_id = event_id
        self._event_users = EventUsers()

        self._raw_details = Setts.details_provider[event_id]
        self._details = {}

    @property
    def event_id(self):
        return self._event_id

    @event_id.setter
    def event_id(self, value):
        """ Set EventId for this class. """
        value = int(value)
        if self._event_id is None:
            self._event_id = value
        elif self._event_id != value:
            log.error(self._error_msg_change, MongoFields.EVENT_ID,
                      self.event_id, self._event_id, value)

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, value):
        """ Set start_time for this class. """
        try:
            value = dateutil.parser.parse(value)
        except AttributeError as e:
            # TODO: add stack
            log.debug(e)
            self._start_time = COUCH_DB_MISSING_TIME
            self._end_time = COUCH_DB_MISSING_TIME
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
        self._couch_raw_db_data = tuple(couch_data)
        # For ease & convenience
        self.couch_data = {int(row.value.get('id', '-1')): row
                           for row in self._couch_raw_db_data}

    def set_missing(self):
        self.description = COUCH_DB_MISSING_DATA
        self.calendar_id = COUCH_DB_MISSING_DATA
        self._start_time = COUCH_DB_MISSING_TIME
        self._end_time = COUCH_DB_MISSING_TIME
        self.duration = COUCH_DB_MISSING_TIME

    @staticmethod
    def get_couch_data(event_ids=None, user_ids=None):
        return Setts._DB_COUCH.value.get_data(event_ids=event_ids,
                                              user_ids=user_ids)

    def __str__(self):
        format_data = {
            'event_id': self.event_id,
            'description': self.description,
            'calendar_id': self.calendar_id,
            'start_time': self.start_time.strftime(STRFTIME_FORMAT),
            'end_time': self.end_time.strftime(STRFTIME_FORMAT),
        }
        return self._str_representation_templ.format(**format_data)

    def __repr__(self):
        txt = 'eventId [%s] users_count [%s] time [%s]-[%s] description [%s]'
        return txt % (self.event_id, len(self.event_users),
                      self.start_time, self.end_time, self.description)


class CaEventOld:
    _event_id = None
    _event_users = None

    # From Couch db
    description = None
    calendar_id = None
    _start_time = None
    _end_time = None
    duration = None

    _couch_raw_db_data = None
    _couch_data = None  # Converted to dict

    # TODO: Proper error handling
    _error_msg_change = ('Tried to change [%s] of the event [%s]! [%s]->[%s]. '
                         'This should never happen. Statistics may be corrupted.')
    _str_representation_templ = (
        '** Event [{event_id}] - [{description}], CalendarId: [{calendar_id}],'
        ' Start/End Time: [{start_time}]/[{end_time}]'
    )

    def __init__(self):
        self._event_users = EventUsers()

    @property
    def event_id(self):
        return self._event_id

    @event_id.setter
    def event_id(self, value):
        """ Set EventId for this class. """
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
        """ Set start_time for this class. """
        try:
            value = dateutil.parser.parse(value)
        except AttributeError as e:
            # TODO: add stack
            log.debug(e)
            self._start_time = COUCH_DB_MISSING_TIME
            self._end_time = COUCH_DB_MISSING_TIME
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
        self._couch_raw_db_data = tuple(couch_data)
        # For ease & convenience
        self.couch_data = {int(row.value.get('id', '-1')): row
                           for row in self._couch_raw_db_data}

    def set_missing(self):
        self.description = COUCH_DB_MISSING_DATA
        self.calendar_id = COUCH_DB_MISSING_DATA
        self._start_time = COUCH_DB_MISSING_TIME
        self._end_time = COUCH_DB_MISSING_TIME
        self.duration = COUCH_DB_MISSING_TIME

    @staticmethod
    def get_couch_data(event_ids=None, user_ids=None):
        return Setts._DB_COUCH.value.get_data(event_ids=event_ids,
                                              user_ids=user_ids)

    def __str__(self):
        format_data = {
            'event_id': self.event_id,
            'description': self.description,
            'calendar_id': self.calendar_id,
            'start_time': self.start_time.strftime(STRFTIME_FORMAT),
            'end_time': self.end_time.strftime(STRFTIME_FORMAT),
        }
        return self._str_representation_templ.format(**format_data)

    def __repr__(self):
        txt = 'eventId [%s] users_count [%s] time [%s]-[%s] description [%s]'
        return txt % (self.event_id, len(self.event_users),
                      self.start_time, self.end_time, self.description)
