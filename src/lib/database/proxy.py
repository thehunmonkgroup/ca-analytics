import collections

from lib.database.stub_data import get_event_stub_data, get_user_stub_data
from lib.extras import Setts


class CaDetailsProvider(collections.MutableMapping):
    _MAX_EVENT_ID = 99999
    _proxy_items = None

    def __init__(self):
        """
        'Before' this proxy we call people the participants, cos it's related
          to event.
        'After' this class (going to DB) we switch the names and call them
          users, as it's related to users of the system.
        +-------+
        | Event |
        +---+---+
            |
            + Participant                 User    +----+
            + Participant \  +-------+  / User    |    |
            + Participant -- | Proxy | -- User -- | DB |
            + ...         /  +-------+  \ ...     |    |
            + ...                                 +----+
        """
        self._proxy_items = {}

    def __delitem__(self, key):
        # @TODO: Check it
        del self._proxy_items[key]

    def __setitem__(self, key, value):
        self._proxy_items[key] = value

    def __len__(self):
        return len(self._proxy_items)

    def __iter__(self):
        return iter(self._proxy_items)

    def __getitem__(self, key):
        """
        We want all CaEvents/CaUsers with the same ids to have same
         details_proxy object, as which we will later propagate them with
         correct values from CouchDB.

        :param key: ID of an event or user.
        :type key: int
        :return:
        """
        try:
            details_proxy = self._proxy_items[int(key)]
            return details_proxy
        except KeyError:
            details_proxy = self._get_proxy_stub(ca_id=key)
            self._proxy_items[key] = details_proxy
            return details_proxy

    @classmethod
    def _get_proxy_stub(cls, ca_id):
        if cls._is_user(ca_id=ca_id):
            details_proxy = get_user_stub_data(user_id=ca_id)
        else:
            details_proxy = get_event_stub_data(event_id=ca_id)
        return details_proxy

    @classmethod
    def _is_user(cls, ca_id):
        return ca_id > cls._MAX_EVENT_ID

    def get_details_from_db(self):
        def get_event_and_user_id_lists():
            evnt_ids, usr_ids = [], []
            for ca_id in self._proxy_items:
                if self._is_user(ca_id=ca_id):
                    usr_ids.append(ca_id)
                else:
                    evnt_ids.append(ca_id)
            return evnt_ids, usr_ids

        event_ids, user_ids = get_event_and_user_id_lists()
        couch_data = Setts._DB_COUCH.value.get_data(event_ids=event_ids,
                                                    user_ids=user_ids)
        for row in couch_data:
            self._proxy_items[int(row.key)].update(row.value)
