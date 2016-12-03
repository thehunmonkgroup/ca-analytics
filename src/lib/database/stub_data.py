def get_event_stub_data():
    return event_stub.copy()


def get_user_stub_data():
    return user_stub.copy()


event_stub = {
    '_id': None,
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
    '_id': None,
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
