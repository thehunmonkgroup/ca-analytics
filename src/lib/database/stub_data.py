from lib.database.engine import EventFields, UserFields
from lib.extras import get_couchdb_id


def get_event_stub_data(event_id):
    selected_event = event_stub.copy()

    # Set ids
    id_filed = selected_event[EventFields.ID_].format(get_couchdb_id(event_id))
    selected_event[EventFields.ID_] = id_filed
    selected_event[EventFields.ID] = event_id

    return selected_event


def get_user_stub_data(user_id):
    selected_user = user_stub.copy()

    id_filed = selected_user[UserFields.ID_].format(user_id)
    selected_user[EventFields.ID_] = id_filed
    selected_user[EventFields.ID] = user_id

    return selected_user


# TODO: Name of fields get from MongoFields. Also event can be generated.
event_stub = {
    '_id': 'event/{}',
    '_rev': None,
    'adminProposedSessions': None,
    'admins': None,
    'calendarId': None,
    'conferenceOverride': None,
    'dateAndTime': None,
    'description': None,
    'duration': None,
    'facilitatorCo': None,
    'facilitatorLead': None,
    'history': None,
    'id': None,
    'muteLock': None,
    'open': None,
    'organizer': None,
    'overflowMessage': None,
    'overflowUserCap': None,
    'previousVideoEmbeds': None,
    'sessionProvider': None,
    'sessionsOpen': None,
    'shortName': None,
    'timeZoneValue': None,
    'title': None,
    'whiteboard': None,
    'youtubeEmbed': None
}

user_stub = {
    'name': {
        'familyName': None,
        'givenName': None
    },
    'superuser': None,
    '_id': 'user/{}',
    'admin': None,
    'link': None,
    'networkList': None,
    'google_json': {
        'name': None,
        'link': None,
        'verified_email': None,
        'picture': None,
        'given_name': None,
        'family_name': None,
        'email': None,
        'id': None,
        'locale': None
    },
    'provider': None,
    'id': None,
    'displayName': None,
    'perms': None,
    'picture': None,
    'isPlusUser': None,
    'emails': None,
    'createdViaHangout': None,
    '_rev': None,
    'preferredContact': None
}
