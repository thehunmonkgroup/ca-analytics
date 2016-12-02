import collections


class CaDetailsProvider(collections.MutableMapping):
    _proxy_items = None

    def __init__(self):
        self._proxy_items = {}

    def __delitem__(self, key):
        pass

    def __setitem__(self, key, value):
        pass

    def __len__(self):
        pass

    def __iter__(self):
        pass

    def __getitem__(self, key):
        pass
