import logging
from pprint import pprint

import couchdb
import dateutil.parser
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from lib.extras import is_string, is_iterable, get_couchdb_id

log = logging.getLogger(__name__)

COUCH_ID = 'id'
COUCH_KEY = 'key'
COUCH_VALUE = 'value'


class MongoFields:
    ID = '_id'
    ACTION = 'action'
    CONNECTED_USERS = 'connectedUsers'
    EVENT_ID = 'eventId'
    LEVEL = 'level'
    MESSAGE = 'message'
    TIMESTAMP = 'timestamp'
    USER_ID = 'userId'


class EventFields:
    ID = 'id'
    ID_ = '_id'
    REV_ = '_rev'

    ADMIN_PROPOSED_SESSIONS = 'adminProposedSessions'
    ADMINS = 'admins'
    CALENDAR_ID = 'calendarId'
    CONFERENCE_OVERRIDE = 'conferenceOverride'
    DATE_AND_TIME = 'dateAndTime'
    DESCRIPTION = 'description'
    DURATION = 'duration'
    FACILITATOR_CO = 'facilitatorCo'
    FACILITATOR_LEAD = 'facilitatorLead'
    HISTORY = 'history'

    MUTE_LOCK = 'muteLock'
    OPEN = 'open'
    ORGANIZER = 'organizer'
    OVERFLOW_MESSAGE = 'overflowMessage'
    OVERFLOW_USER_CAP = 'overflowUserCap'
    PREVIOUS_VIDEO_EMBEDS = 'previousVideoEmbeds'
    SESSION_PROVIDER = 'sessionProvider'
    SESSIONS_OPEN = 'sessionsOpen'
    SHORT_NAME = 'shortName'
    TIME_ZONE_VALUE = 'timeZoneValue'
    TITLE = 'title'
    WHITEBOARD = 'whiteboard'
    YOUTUBE_EMBED = 'youtubeEmbed'


class UserFields:
    ID = 'id'
    ID_ = '_id'
    REV_ = '-rev'

    ADMIN_PROPOSED_SESSIONS = 'adminProposedSessions'
    ADMIN = 'admin'
    CREATED_VIA_HANGOUT = 'createdViaHangout'
    DISPLAY_NAME = 'displayName'
    EMAILS = 'emails'

    GOOGLE_JSON = 'google_json'
    G_FAMILY_NAME = 'family_name'
    G_EMAIL = 'email'
    G_GIVEN_NAME = 'given_name'
    G_ID = 'id'
    G_LINK = 'link'
    G_LOCALE = 'locale'
    G_NAME = 'name'
    G_PICTURE = 'picture'
    G_VERIFIED_EMAIL = 'verified_email'

    IS_PLUS_USER = 'isPlusUser'
    LINK = 'link'
    NETWORK_LIST = 'networkList'

    NAME = 'name'
    FAMILY_NAME = 'familyName'
    GIVEN_NAME = 'givenName'

    PERMS = 'perms'
    CREATE_EVENTS = 'createEvents'
    JOIN_EVENTS = 'joinEvents'

    PICTURE = 'picture'
    PREFERRED_CONTACT = 'preferredContact'
    PROVIDER = 'provider'
    SUPERUSER = 'superuser'


class MongoData:
    _filter_join_events = {'action': 'join', 'message': 'events'}
    _TIME_TEMPLATE = '%sT00:00:00.000Z'
    db_mongo = None

    def __init__(self, connection_string, database_name,
                 check_db_connection_timeout=5):
        def check_database_connection():
            try:
                client = MongoClient(
                    connection_string,
                    serverSelectionTimeoutMS=check_db_connection_timeout
                )
                client.server_info()
            except ServerSelectionTimeoutError:
                log.error("Couldn't connect to MongoDB [%s]. Exiting.",
                          connection_string)
                exit(1)

        check_database_connection()
        self._client = MongoClient(connection_string)
        self.db_mongo = self._client[database_name]

    @classmethod
    def filter_date(cls, data, date_from=None, date_to=None):
        """
            114498861474704307604: 2016-03-22T02:05:03.806Z
            108960323403366113062: 2016-03-23T09:50:41.085Z
            104697518485852908489: 2016-03-28T22:10:57.527Z
            111235421902528084263: 2016-04-06T23:04:25.075Z
            108611793445678484173: 2016-04-23T18:56:08.241Z
            109430383226686017839: 2016-04-27T14:43:45.471Z
            100958096234392941059: 2016-05-09T21:13:35.969Z
            113213949010558579212: 2016-05-11T18:25:43.205Z
            102365267464342191906: 2016-05-23T16:56:44.571Z
            116488113102013485647: 2016-06-17T02:18:44.882Z
            102983352577771866921: 2016-06-19T22:20:29.827Z
            106432116677569148829: 2016-06-30T19:25:04.165Z
            116156233828749181787: 2016-07-02T15:35:20.402Z
        :param date_from:
        :param date_to:
        :return:
        """

        def handle_both(date_from, date_to):
            ret_f = []
            date_from_orig = date_from
            date_to_orig = date_to
            date_from = dateutil.parser.parse(cls._TIME_TEMPLATE % date_from)
            date_to = dateutil.parser.parse(cls._TIME_TEMPLATE % date_to)

            if date_from > date_to:
                raise RuntimeError(
                    'Date from "%s" is earlier than date to "%s".' % (
                        date_from_orig, date_to_orig))
            elif date_from_orig == date_to_orig:
                raise RuntimeError(
                    'Date_from "%s" is the same as date_to "%s". '
                    'If results should include only one day, '
                    'set date_to to date_from+1day. ' % (
                        date_from_orig, date_to_orig))
            for row in data:
                try:
                    log_date = dateutil.parser.parse(row['timestamp'])
                    if date_from < log_date < date_to:
                        ret_f.append(row)
                except KeyError as e:
                    log.error("Couldn't determine logs date [%s] Error [%s]",
                              row, e)
            return ret_f

        def handle_from(date_from):
            ret_f = []
            date_from = dateutil.parser.parse(cls._TIME_TEMPLATE % date_from)
            for row in data:
                try:
                    log_date = dateutil.parser.parse(row['timestamp'])
                    if date_from < log_date:
                        ret_f.append(row)
                except KeyError as e:
                    log.error("Couldn't determine logs date [%s] Error [%s]",
                              row, e)
            return ret_f

        def handle_to(date_to):
            ret_f = []
            date_to = dateutil.parser.parse(cls._TIME_TEMPLATE % date_to)
            for row in data:
                try:
                    log_date = dateutil.parser.parse(row['timestamp'])
                    if log_date < date_to:
                        ret_f.append(row)
                except KeyError as e:
                    log.error("Couldn\'t determine logs date [%s] Error [%s]",
                              row, e)
            return ret_f

        ret = data
        if date_from is None and date_to is None:
            pass
        elif date_from and date_to:
            ret = handle_both(date_from, date_to)
        elif date_from:
            ret = handle_from(date_from)
        elif date_to:
            ret = handle_to(date_to)
        return ret

    def get_data(self, event_ids=None, user_ids=None):
        """
        Get data about specific events or users.

        :param user_ids:
        :param user_ids: list of userIds
        :type event_ids: list of eventIds
        :return:
        """
        question = self.filter_join_events

        if event_ids is not None:
            question["eventId"] = self._search_in(event_ids)
        if user_ids is not None:
            question["userId"] = self._search_in(user_ids, cast=str)
        # Else whole db is downloaded for 'action': 'join'

        ret = list(self.db_mongo.analytics.find(question))
        return ret

    @property
    def filter_join_events(self):
        return self._filter_join_events.copy()

    @staticmethod
    def _search_in(iterable, cast=int):
        """
        Return dict that will allow several fields to be searched against.
        DB is type (str, int, ..) sensitive.

        with userId:
        OverflowError: MongoDB can only handle up to 8-byte ints
        """
        ret = []
        for each in iterable:
            try:
                ret.append(cast(each))
            except Exception as e:
                log.error('Could not convert value "%s" to type "%s"\n%s',
                          each, type(cast), e)
        return {'$in': ret}


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
