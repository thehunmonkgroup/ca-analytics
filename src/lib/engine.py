import logging

from lib.database import MongoFields
from lib.event import CaEvent
from lib.extras import Setts

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
                             'action': 'join'|'leave',
                             '_id': ObjectId('57a3a39800c88030ca43b777')},
                             {..},
                             {..},
                          ]
    :return:
    """
    ca_events_holder = {}
    for log_entry in selected_logs:
        event_id = log_entry[MongoFields.EVENT_ID]
        try:
            ca_event = ca_events_holder[event_id]
        except KeyError:
            ca_event = CaEvent(event_id=event_id)
            ca_events_holder[event_id] = ca_event
        ca_event.add(log_entry=log_entry)

    Setts.details_provider.get_details_from_db()

    return sort_output_events(event_list=ca_events_holder.values())


def sort_output_events(event_list):
    return sorted(event_list, key=Setts.ORDER_BY.event_sort_keys)
