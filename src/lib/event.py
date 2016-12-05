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
from lib.participants import ParticipantsHandler

log = logging.getLogger(__name__)


class CaEvent:
    _event_id = None

    # Details
    _calendar_id = None
    _description = None
    _start_time = None
    _end_time = None

    # Handle participants
    _event_participants = None
    add = None  # It'll be _event_participants.add

    # Details storage variables
    _raw_details = None
    _details = None  # Cache of converted values

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
        """
        _raw_details must contain stub of CouchDB info. Dict with None values.

        :param event_id:
        """
        # Setup event
        self.event_id = event_id
        self._raw_details = Setts.details_provider[event_id]

        # Setup users
        self._event_participants = ParticipantsHandler()
        self.add = self._event_participants.add

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
            log.warning('Error converting [%s] to date object for event [%s]. '
                        'Returning start_date as [%s]. \n %s',
                        raw_value, self.event_id, self._start_time, e)
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
            log.warning('Error estimating end time for the event [%s]. '
                        'Start_time [%s], duration [%s], end_time [%s].\n %s',
                        self.event_id, self.start_time, duration,
                        self._end_time, e)
        return self._end_time

    @property
    def end_time_str(self):
        try:
            return self.end_time.strftime(STRFTIME_FORMAT)
        except Exception as e:
            log.debug(e)
            return str(self._start_time)

    def event_participants(self, sort_by=None):
        return self._event_participants.unique

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
        return txt % (self.event_id, len(self.event_participants()),
                      self.start_time_str, self.end_time_str, self.description)
