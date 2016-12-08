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
