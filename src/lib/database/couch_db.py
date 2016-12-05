import logging
from pprint import pprint

import couchdb

from lib.extras import is_string, is_iterable, get_couchdb_id

log = logging.getLogger(__name__)


class CouchData:
    QUERY_EVENT = '''
        function(doc){
            var patt = new RegExp('^event/[0-9]{5}$');
            if(patt.test(doc._id) && doc.id == %s){
                emit(doc.id, doc);
            }
        }
        '''
    QUERY_LIST = '''
        function(doc){
            var L = function() {
                    var obj = {};
                    for(var i=0; i<arguments.length; i++)
                        obj[arguments[i]] = null;

                    return obj; };

            if(doc._id in L('%s')){
                emit(doc.id, doc);
            }
        }
        '''
    db_couch = None

    def __init__(self, connection_string, database_name):
        self._client = couchdb.Server(connection_string)
        try:
            self.db_couch = self._client[database_name]
        except ConnectionRefusedError:
            log.error("Couldn't connect to CouchDB %s. Exiting.",
                      {'connection_string': connection_string,
                       'database_name': database_name})
            exit(1)

    def get_data(self, event_ids=None, user_ids=None):
        """
        Get data about specific events or users.

        :version: 2016.11.11
        :param user_ids:
        :param user_ids: list of userIds
        :type event_ids: list of eventIds
        :return:
        """

        def make_iterable(evnt_ids=event_ids, usr_ids=user_ids):
            # Correctness of ids is checked later

            if is_string(val=evnt_ids) or not is_iterable(val=evnt_ids):
                log.debug('Converting to iterable evnt_ids: %s', evnt_ids)
                evnt_ids = [evnt_ids]

            if is_string(val=usr_ids) or not is_iterable(val=usr_ids):
                log.debug('Converting to iterable usr_ids: %s', usr_ids)
                usr_ids = [usr_ids]
            return evnt_ids, usr_ids

        def get_search_values(evnt_ids, usr_ids):
            """
            Prepares search entries for CoachDB.
             * converts elements of lists to string
             * deduplicate ids for events and users
             * fills till 5 chars on event_ids
             * sorts them
             * Returns

            :param evnt_ids:
            :param usr_ids:
            :return:
            """

            def none_or_empty(val):
                """
                Event or user id can be 0.

                :param val:
                :return:
                """
                # TODO: I think it was changed and now we are passing always
                #   string. So maybe no need for this.
                #   Generally refactor and unify str/int ids/keys from db in
                #   our models.
                return val in ('None', '')

            evnt_templ = 'event/%s'
            usr_templ = 'user/%s'

            ret = []
            for evnt in sorted(set(map(str, evnt_ids))):
                if none_or_empty(val=evnt):
                    continue
                ret.append(evnt_templ % get_couchdb_id(event_id=evnt))

            for usr in sorted(set(map(str, usr_ids))):
                if none_or_empty(val=usr):
                    continue
                ret.append(usr_templ % usr)

            return ret

        # TODO: logging!
        # TODO: Import make_iterable from extras
        event_ids, user_ids = make_iterable(evnt_ids=event_ids,
                                            usr_ids=user_ids)

        search_vals = get_search_values(evnt_ids=event_ids, usr_ids=user_ids)
        search_query = self.QUERY_LIST % "', '".join(search_vals)

        results = self.db_couch.query(search_query)
        pprint(results.rows)
        return results.rows
