import logging

import dateutil.parser
import dateutil.relativedelta

from lib.database import (
    EventFields,
    MongoFields
)
from lib.extras import (
    Setts,
    STRFTIME_FORMAT,
)
from lib.participants import EventParticipantsHandler

log = logging.getLogger(__name__)


class CaEvent:
    _event_id = None

    # Details
    _calendar_id = None
    _description = None
    _start_time = None
    _end_time = None

    # Handle participants
    _participants_handler = None
    add_participant = None  # It'll be _event_participants.add

    # Details storage variables
    _raw_details = None
    _details = None  # Cache of converted values

    # TODO: Proper error handling
    _error_msg_change = (
        'Tried to change [%s] of the event [%s]! [%s]->[%s]. '
        'This should never happen. Statistics may be corrupted.'
    )
    _error_msg_start_time = (
        'Start_date and probably all details for event [%s] are missing '
        'in CouchDB. Using first connected participant timestamp [%s] '
        'as event start_date. Original error [%s]'
    )
    _error_msg_end_time = (
        'End_time estimation error for the event [%s] due to details lack '
        'in CouchDB. '
        'Using last connected participant timestamp [%s] as estimated '
        'event end_date. '
        'Start_time [%s], estimated duration [%s], end_time [%s]. '
        'Original error [%s]'
    )

    _str_representation_templ = (
        '** Event [{event_id}] - [{description}], CalendarId: [{calendar_id}],'
        ' Start/End Time: [{start_time}]/[{end_time}]'
    )

    _silenced_exceptions = set()

    def __init__(self, event_id):
        """
        _raw_details must contain stub of CouchDB info. Dict with None values.

        :param event_id:
        """
        # Setup event
        self.event_id = event_id
        self._raw_details = Setts.details_provider[event_id]

        # Setup users
        self._participants_handler = EventParticipantsHandler()
        self.add_participant = self._participants_handler.add

    @property
    def event_id(self):
        return self._event_id

    @event_id.setter
    def event_id(self, value):
        value = int(value)
        if self._event_id is None:
            self._event_id = value
        elif self._event_id != value:
            log.warning(self._error_msg_change, MongoFields.EVENT_ID,
                        self.event_id, self._event_id, value)

    @property
    def calendar_id(self):
        if self._calendar_id is not None:
            return self._calendar_id
        self._calendar_id = self._raw_details[EventFields.CALENDAR_ID]
        return self._calendar_id

    @property
    def description(self):
        if self._description is not None:
            return self._description
        self._description = self._raw_details[EventFields.DESCRIPTION]
        return self._description

    @property
    def start_time(self):
        """
        Return start time for this event.

        :param raw_value: '2016-05-12T19:00:00+00:00'
        :return:
        """
        if self._start_time is not None:
            return self._start_time

        raw_value = self._raw_details[EventFields.DATE_AND_TIME]
        try:
            self._start_time = dateutil.parser.parse(raw_value)
        except AttributeError as e:
            first_timestamp = self._participants_handler.all_timestamps[0]
            self._start_time = first_timestamp

            log_handler = self._get_log_handler(
                exception_key=(self.event_id, self._error_msg_start_time))
            log_handler(self._error_msg_start_time,
                        self.event_id,
                        self.start_time_str, e)
        return self._start_time

    @property
    def start_time_str(self):
        try:
            return self.start_time.strftime(STRFTIME_FORMAT)
        except Exception as e:
            log.debug(e)
            return str(self._start_time)

    @property
    def end_time(self):
        if self._end_time is not None:
            return self._end_time

        duration = self._raw_details[EventFields.DURATION]
        try:
            dt = dateutil.relativedelta.relativedelta(minutes=duration)
            self._end_time = self.start_time + dt
        except TypeError as e:
            # TODO: When leave time will be implemented for the users,
            #       change it to the last user leaving
            last_timestamp = self._participants_handler.all_timestamps[-1]
            self._end_time = last_timestamp
            duration = self._end_time - self.start_time

            log_handler = self._get_log_handler(
                exception_key=(self.event_id, self._error_msg_end_time))
            log_handler(self._error_msg_end_time,
                        self.event_id, self.end_time_str, self.start_time_str,
                        duration, self.end_time_str, e)
        return self._end_time

    @property
    def end_time_str(self):
        try:
            return self.end_time.strftime(STRFTIME_FORMAT)
        except Exception as e:
            log.debug(e)
            return self.start_time_str

    def event_participants(self):
        return self._participants_handler.get_participants()
        # return self._participants_handler.unique

    @property
    def participants_number(self):
        return len(self.event_participants())

    @classmethod
    def _get_log_handler(cls, exception_key):
        """
        We want to let user know only with the first message that there is
         something wrong. The rest can be silenced.

        :param exception_key:
        :return:
        """
        if exception_key in cls._silenced_exceptions:
            return log.debug
        else:
            cls._silenced_exceptions.add(exception_key)
            return log.warning

    def __str__(self):
        format_data = {
            'event_id': self.event_id,
            'description': self.description,
            'calendar_id': self.calendar_id,
            'start_time': self.start_time_str,
            'end_time': self.end_time_str,
        }
        return self._str_representation_templ.format(**format_data)

    def __repr__(self):
        txt = 'eventId [%s] users_count [%s] time [%s]-[%s] description [%s]'
        return txt % (self.event_id, self.participants_number,
                      self.start_time_str, self.end_time_str, self.description)
