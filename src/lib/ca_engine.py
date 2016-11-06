#!/usr/bin/env python3
# (c) 2016 Alek
#  Engine for ca analytics
import collections
import logging

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
    ret = sorted(events.values(), key=lambda x: x.e_id)

    fill_couchdb_info(ca_events_list=ret)
    return ret


class CaUser:
    pass


class CaEvent:
    e_id = None
    _couch_data = None
    _mongo_data = None
    _user_list = None

    @property
    def user_list(self):
        return self._user_list

    @user_list.setter
    def user_list(self, value):
        if self._user_list is None:
            self._user_list = [value]
        else:
            self._user_list.append(value)

    def append(self, log_entry):
        self.set_e_id(e_id=log_entry['eventId'])
        self.user_list = log_entry

    def set_e_id(self, e_id):
        """ Sets EventId for this class. """
        # TODO: Make property of it?
        if self.e_id is None:
            self.e_id = e_id
        elif self.e_id != e_id:
            log.error('Tried to change e_id of the class! [%s]->[%s]. '
                      'This should never happen. Results may be corrupted.',
                      self.e_id, e_id)

    def fill_with_couch_details(self):
        # TODO: Get CouchDB details about event and users
        pass

    def __str__(self):
        return 'eventId [%s] user_list %s' % (self.e_id, self.user_list)
