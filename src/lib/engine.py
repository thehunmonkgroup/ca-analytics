import collections
import logging

from lib.database.engine import MongoFields
from lib.event import CaEvent

log = logging.getLogger(__name__)


def get_ca_event_list(selected_logs):
    """
    Return [CaEvent(), CaEvent(), ...]

    :param selected_logs: [ {'eventId': 430,
                             'userId': '116777777777777758951',
                             'level': 'info',
                             'message': 'events',
                             'timestamp': '2016-05-26T16:37:46.106Z',
                             'connectedUsers': 5,
                             'action': 'join',
                             '_id': ObjectId('57a3a39800c88030ca43b777')},
                             {..},
                             {..},
                          ]
    :return:
    """

    ca_event_selector = {}
    for log_entry in selected_logs:
        event_id = log_entry[MongoFields.EVENT_ID]
        ca_event = ca_event_selector.get(event_id, CaEvent(event_id=event_id))
        print(log_entry)

        # Effective deduplication mechanism
        # events = collections.defaultdict(CaEvent)
        # # TODO: Implicitly initialize CaEvent with eventId - we need get proxy obj
        #
        # for row in selected_logs:
        #     eventId = row['eventId']
        #     events[eventId].append(log_entry=row)
        #
        # # Get rid of dict, and sort events by id
        # ret = sorted(events.values(), key=lambda x: x.event_id)
        #
        # # TODO: Can be done in a more elegant way?
        # fill_couchdb_info(ca_events_list=ret)
        # return ret


def get_ca_events_old(db_data):
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
    # TODO: Implicitly initialize CaEvent with eventId - we need get proxy obj

    for row in db_data:
        eventId = row['eventId']
        events[eventId].append(log_entry=row)

    # Get rid of dict, and sort events by id
    ret = sorted(events.values(), key=lambda x: x.event_id)

    # TODO: Can be done in a more elegant way?
    fill_couchdb_info(ca_events_list=ret)
    return ret
