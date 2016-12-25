from example_data import User111, User222, Event111, Event222
from lib.extras import make_iterable


class ResponseFactory:
    NOT_CALLED = 'not called'
    sample_users = [
        User111,
        User222
    ]
    sample_events = [
        Event111,
        Event222
    ]

    @classmethod
    def get_all_users_attending_event(cls, event_id):
        ret = []

        def user_attended(usr):
            for event_attended in usr._participated_in:
                if event_attended.event_id == event_id:
                    return True
            return False

        for user in cls.sample_users:
            if user_attended(user):
                ret.append(user)

        return ret

    @classmethod
    def get_users_for_given_event_class(cls, event_list):
        """
        Retrun dict:
            {Event_class: [User1, User2, ..], ...], Event_2: [], }
        :param event_list: List of Sample event class
        :return:
        """
        ret = {}
        for event_class in event_list:
            users = cls.get_all_users_attending_event(event_id=event_class.eventId)
            ret[event_class] = users
        return ret

    @classmethod
    def get_all_mongo_logs(cls):
        ret = []
        for sample_user in cls.sample_users:
            ret.extend(sample_user.get_mongo_response())
        return ret

    @classmethod
    def get_all_couch_responses(cls):
        ret = []
        for sample_user in cls.sample_users:
            ret.append(sample_user.get_couch_mock())
        for sample_event in cls.sample_events:
            ret.append(sample_event.get_couch_mock())
        return ret

    @classmethod
    def mongo_get_data_side_effect(cls, event_ids=NOT_CALLED,
                                   user_ids=NOT_CALLED):
        # print('called mongo_side_effect with:', {'event_ids': event_ids,
        #                                          'user_ids': user_ids})

        event_ids, user_ids = make_iterable(evnt_ids=event_ids,
                                            usr_ids=user_ids)
        ret = [entry for entry in cls.get_all_mongo_logs()
               if entry['eventId'] in event_ids or entry['userId'] in user_ids]
        return ret

    @classmethod
    def couch_get_data_side_effect(cls, event_ids=NOT_CALLED,
                                   user_ids=NOT_CALLED):
        # print('called couch_side_effect with:', {'event_ids': event_ids,
        #                                          'user_ids': user_ids})

        event_ids, user_ids = make_iterable(evnt_ids=event_ids,
                                            usr_ids=user_ids)
        # Default value is None or string from it
        selected_ids = [each for each in event_ids + user_ids
                        if each not in ('None', None)]

        # Check if row is for what we've asked
        ret = [row for row in cls.get_all_couch_responses()
               if row.key in selected_ids]
        return ret
