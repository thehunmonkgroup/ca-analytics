from lib.extras import Setts
from .engine import (MongoData, CouchData)
from .proxy import CaDetailsProvider


def init_db():
    Setts._DETAILS_PROVIDER.value = CaDetailsProvider()

    Setts._DB_MONGO.value = MongoData(
        connection_string=Setts.MONGO_STRING.value,
        database_name=Setts.MONGO_DATABASE.value
    )
    Setts._DB_COUCH.value = CouchData(
        connection_string=Setts.COUCH_STRING.value,
        database_name=Setts.COUCH_DATABASE.value
    )
