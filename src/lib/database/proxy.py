import collections

from lib.database.stub_data import get_event_stub_data, get_user_stub_data


class CaDetailsProvider(collections.MutableMapping):
    _MAX_EVENT_ID = 99999
    _proxy_items = None

    def __init__(self):
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
        if ca_id > cls._MAX_EVENT_ID:
            details_proxy = get_user_stub_data(user_id=ca_id)
        else:
            details_proxy = get_event_stub_data(event_id=ca_id)
        return details_proxy

    def get_details_from_db(self):
        print('Downloading data from CouchDB')
        print('List of ids to ask:', list(self._proxy_items.keys()))
