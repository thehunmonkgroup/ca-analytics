import argparse
import collections
import csv
import errno
import functools
import json
import logging
import operator
import os
import time
from collections import OrderedDict
from os.path import join as j

import ruamel.yaml as yaml

log = logging.getLogger(__name__)

is_string = lambda val: isinstance(val, str)
is_iterable = lambda val: isinstance(val, collections.Iterable)
# TODO: Create base CaClass, place it there and add err silencing there too
STRFTIME_FORMAT = '%Y-%m-%d %H:%M:%S'
CSV_FIELDNAMES = ('Event_ID', 'Description',
                  'Calendar_ID', 'Start_time',
                  'End_time', 'User_ID',
                  'User_name', 'Join_time', 'Leave_time')


def make_iterable(evnt_ids='None', usr_ids='None'):
    # Correctness of ids is checked later
    if is_string(val=evnt_ids) or not is_iterable(val=evnt_ids):
        log.debug('Converting to iterable evnt_ids: %s', evnt_ids)
        evnt_ids = [evnt_ids]
    if is_string(val=usr_ids) or not is_iterable(val=usr_ids):
        log.debug('Converting to iterable usr_ids: %s', usr_ids)
        usr_ids = [usr_ids]
    return evnt_ids, usr_ids


def get_couchdb_id(event_id):
    return str(event_id).rjust(5, '0')


class OutputHandler:
    _ca_events_list = None
    _lines = None
    _user_print_templ = '  %s'

    def __init__(self, ca_events_list):
        """
        Here is raw data. During printing/writing to file it's converted in
        `_prepare_output`.:
        """
        self._ca_events_list = ca_events_list
        if not ca_events_list:
            print('Output created with settings: "%s"' % Setts.cfg)
            self._lines = ['No data to print.']

    @property
    def lines(self):
        """ List of lines to be written to output. """
        if self._lines is None:
            # print('Output created with settings: "%s"' % Setts.cfg)
            self._lines = self.convert_to_string_output()
        return self._lines

    def convert_to_string_output(self):
        out = []
        for each_ca_event in self._ca_events_list:
            out.append(str(each_ca_event))
            user_list = [self._user_print_templ % str(usr) for usr
                         in each_ca_event.event_participants()]
            out.extend(user_list)
            out.append('')

        return out

    def write_terminal(self):
        for line in self.lines:
            print(line)

    def write_file(self, f_path):
        f_path = norm_path(f_path, mkfile=False, mkdir=False)
        with open(f_path, 'w') as f:
            print('* Writing to file: "%s"' % f_path)
            f.write('\n'.join(self.lines))
            print('* Done')

    def write_csv(self, f_path):
        f_path = norm_path(f_path, mkfile=False, mkdir=False)

        with open(f_path, 'w') as f:
            print('* Exporting as: "%s"' % f_path)
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES,
                                    extrasaction='ignore',
                                    quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            for each_ca_event in self._ca_events_list:
                try:
                    event_dict = self.convert_to_dictionary(each_ca_event)
                    for user in event_dict['Users']:
                        event_dict['User_ID'] = user['User_ID']
                        event_dict['User_name'] = user['User_name']
                        event_dict['Join_time'] = user['Join_time']
                        event_dict['Leave_time'] = user['Leave_time']
                        writer.writerow(event_dict)
                except Exception as e:
                    log.error(
                        'Encountered error while exporting event [%s] to csv. '
                        'Skipping that row. Caused by: "%s"',
                        each_ca_event.event_id, e)
            print('* Done')

    def write_json(self, f_path):
        print('* Exporting as: "%s"' % f_path)
        f_path = norm_path(f_path, mkfile=False, mkdir=False)
        with open(f_path, 'w') as f:
            export_list = []
            for each_ca_event in self._ca_events_list:
                event_dict = self.convert_to_dictionary(each_ca_event)
                export_list.append(event_dict)
            json.dump(export_list, f, sort_keys=False)
            print('* Done')

    @classmethod
    def convert_to_dictionary(cls, event):
        out = {'Event_ID': event.event_id,
               'Description': event.description,
               'Calendar_ID': event.calendar_id,
               'Start_time': event.start_time_str,
               'End_time': event.end_time_str}
        users = [{'User_ID': user.user_id,
                  'User_name': user.display_name,
                  'Join_time': user.timestamp_str.join,
                  'Leave_time': user.timestamp_str.leave}
                 for user in event.event_participants()]
        out['Users'] = users
        return out


def norm_path(path, mkdir=True, mkfile=False, logger=None):
    """
    Normalize path and, optionally, makes it.
    If mkfile=True everything after last '/' is treated as file and touched.
    If you want only create dirs to that file, without creating it,
      use: os.path.split(pth)[0]

    Version: 2016.08.06
    :param path:
    :param mkdir: mkdir(os.path.split[0])
    :param mkfile: touch(path)
    :param logger:
    :return:
    """

    def touch(fname, times=None):
        """
        version: 2015.09.15
        version: 1
        :param fname:
        :param times:
        :return:
        """
        with open(fname, 'a') as _:
            os.utime(fname, times)

    def _mkdir(pth):
        try:
            os.makedirs(pth)
            logger.debug('dir made [%s]', pth)
        except OSError as exception:
            logger.debug(exception)
            if exception.errno != errno.EEXIST:
                raise

    def _mkfile(pth):
        dirs = os.path.split(pth)[0]
        _mkdir(dirs)
        touch(pth)
        logger.debug('file touched [%s]', pth)

    if logger is None:
        logger = logging.getLogger('dummy')
    logger.debug('Normalizing [%s] with %s', path,
                 {'mkdir': mkdir, 'mkfile': mkfile})
    if not isinstance(path, str):
        path = j(*path)
    path_org = path
    path = os.path.normpath(os.path.expanduser(os.path.expandvars(path)))

    if not os.path.exists(path):
        if mkfile:
            _mkfile(path)
        elif mkdir:
            _mkdir(path)

    logger.debug('Normalized [%s] -> [%s]', path_org, path)
    return path


def conf_logs(log_name, log_dir=None, console_level=logging.ERROR,
              file_level=logging.DEBUG, print_dest=False,
              esb_log_dir=None):
    """
    :version: 2016.07.17 (make dummy to work)
    :param log_name:
    :param log_dir:
    :param console_level:
    :param file_level:
    :param print_dest:
    :param esb_log_dir: dir path to where esb.log file should be stored
                                                    {esb_log_dir}/{esb_name}.log
    :return:
    """
    from logging import handlers

    msg_esb = ''
    msg_file = ''

    console_handle = logging.StreamHandler()
    console_handle.setLevel(console_level)
    console_fmter = logging.Formatter('[%(funcName)s]: %(message)s')
    console_handle.setFormatter(console_fmter)
    log_handlers = [console_handle]

    file_format = logging.Formatter(
        '%(asctime)s %(levelname)-8s [%(funcName)s]: %(message)s')

    if esb_log_dir:
        esb_name = 'esb'
        esb_dest = norm_path((esb_log_dir,
                              '{esb_name}.log'.format(esb_name=esb_name)),
                             mkfile=True)
        esb_file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=esb_dest, when='midnight', backupCount=30)
        esb_file_handler.setFormatter(file_format)
        esb_file_handler.setLevel(logging.DEBUG)

        esb_log = logging.getLogger(esb_name)
        esb_log.setLevel(logging.DEBUG)
        for handler in esb_log.handlers[:]:  # Make a copy of the list
            # Close files, but not stdout/stderr
            if not type(handler) is logging.StreamHandler:
                handler.stream.close()
                esb_log.removeHandler(handler)
        esb_log.addHandler(esb_file_handler)
        esb_log.propagate = False
        msg_esb = ' esb_dest: "%s"' % esb_dest

    if log_dir:
        f_log_name = '%s.log' % log_name
        f_log_pth = norm_path(j(log_dir, f_log_name), mkfile=True)

        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=f_log_pth, when='midnight', backupCount=30)

        file_handler.setFormatter(file_format)
        file_handler.setLevel(file_level)
        log_handlers.append(file_handler)
        msg_file = ' file_log_dest: "%s", file_level: "%s"' % (f_log_pth,
                                                               file_level)
    root_log = logging.getLogger()
    if log_dir and file_level < console_level:
        root_log.setLevel(level=file_level)
    else:
        root_log.setLevel(level=console_level)

    for handler in root_log.handlers[:]:  # Make a copy of the list
        # Close files, but not stdout/stderr
        if not type(handler) is logging.StreamHandler:
            handler.stream.close()
        root_log.removeHandler(handler)
    for h in log_handlers:
        root_log.addHandler(h)

    dummy = logging.getLogger('dummy')
    dummy.handlers = []
    dummy.addHandler(logging.NullHandler())
    dummy.propagate = False

    msg = 'Logs configured with: console_level: "%s"%s%s' % (
        console_level, msg_file, msg_esb)
    if print_dest:
        print(msg)
    log.debug(msg)


def configure_argparse(rwd, start_cmd=None):
    """
    :return
    Namespace(
        cfg=None,
        couchdb_connection_string=None,
        couchdb_database=None,
        date_from=None,
        date_to=None,
        order_by: eventId,
        event=None,
        log=None,
        mongo_database=None,
        mongodb_connection_string=None,
        output_destination=None,
        user=None
    )
    """
    # TODO: Move it to inside/get from setts class
    parser = argparse.ArgumentParser(
        description='Exports Circle Anywhere analytical information',
        add_help=False,
        usage=('%(prog)s '
               '[-e [EVENT_ID [EVENT_ID ...]]] '
               '[-u [USER_ID [USER_ID ...]]] '
               '[--date_from DATE] '
               '[--date_to DATE] '
               '[--order_by [{}]] '
               '[CONFIGURATION] [-h]').format('|'.join(Setts.ORDER_BY.choices))
    )

    stats_opt = parser.add_argument_group('Analytics Options')

    stats_opt.add_argument('-e', '--' + Setts.EVENT.key,
                           help=Setts.EVENT.desc,
                           metavar='EVENT_ID',
                           type=int,
                           nargs='*',
                           )

    stats_opt.add_argument('-u', '--' + Setts.USER.key,
                           help=Setts.USER.desc,
                           metavar='USER_ID',
                           type=int,
                           nargs='*',
                           )

    stats_opt.add_argument('--' + Setts.DATE_FROM.key,
                           help=Setts.DATE_FROM.desc,
                           metavar='DATE',
                           type=str,
                           )

    stats_opt.add_argument('--' + Setts.DATE_TO.key,
                           # default=Setts.DATE_TO.default,
                           help=Setts.DATE_TO.desc,
                           metavar='DATE',
                           type=str,
                           )

    stats_opt.add_argument('--' + Setts.ORDER_BY.key,
                           help=Setts.ORDER_BY.desc,
                           metavar='SORT_KEY',
                           choices=list(Setts.ORDER_BY.choices),
                           type=str,
                           nargs='*',
                           )

    conn_opt = parser.add_argument_group('Connection Options')

    conn_opt.add_argument('--' + Setts.COUCH_STRING.key,
                          type=str,
                          help=Setts.COUCH_STRING.desc,
                          metavar='URL',
                          )

    conn_opt.add_argument('--' + Setts.COUCH_DATABASE.key,
                          type=str,
                          help=Setts.COUCH_DATABASE.desc,
                          metavar='NAME',
                          )

    conn_opt.add_argument('--' + Setts.MONGO_STRING.key,
                          type=str,
                          help=Setts.MONGO_STRING.desc,
                          metavar='URI',
                          )

    conn_opt.add_argument('--' + Setts.MONGO_DATABASE.key,
                          type=str,
                          help=Setts.MONGO_DATABASE.desc,
                          metavar='NAME',
                          )

    conf_opt = parser.add_argument_group('Configuration')

    conf_opt.add_argument('-o', '--' + Setts.OUT_DEST.key,
                          type=str,
                          help=Setts.OUT_DEST.desc,
                          metavar='FILE',
                          )

    conf_opt.add_argument('-c', '--' + Setts.CFG_PATH.key,
                          type=str,
                          default=Setts.CFG_PATH.default % rwd,
                          help=Setts.CFG_PATH.desc % rwd,
                          metavar='FILE',
                          )

    conf_opt.add_argument('-l', '--' + Setts.LOG_PATH.key,
                          type=str,
                          help=Setts.LOG_PATH.desc,
                          metavar='FILE',
                          )

    conf_opt.add_argument('-h', '--help',
                          action='help',
                          default=argparse.SUPPRESS,
                          help='Print this help text and exit',
                          )
    args = parser.parse_args(args=start_cmd)
    return args, parser


def timeit(func):
    @functools.wraps(func)
    def newfunc(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        elapsed_time = time.time() - start_time

        msg = 'Function [{name}] finished in [{ms}ms] ~[{min}:{sec}]min'
        minutes, seconds = divmod(elapsed_time, 60)
        format_args = {'name': func.__name__,
                       'ms': int(elapsed_time * 1000),
                       'min': int(minutes),
                       'sec': int(seconds)}
        print(msg.format(**format_args))

    return newfunc


class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class Setts:
    # If args are validated, the default option should always be set
    value = None

    class _Option:
        def __init__(self, key, value=None, default=None, desc='',
                     callback=None):
            """
            :version: 2016.07.14
            """
            self.key = key
            self.default = default
            self.callback = callback
            self.desc = desc
            self.value = value

        def __repr__(self):
            return ('Option(key=%s, '
                    'value=%s, '
                    'default=%s, '
                    'desc="%s", '
                    'callback=%s)' % (self.key, self.value, self.default,
                                      self.desc, self.callback))

        def __str__(self):
            return '"%s": "%s"' % (self.key, self.value)

    class _OrderByOpt(_Option):
        # Available argument names to pass to the program for sorting
        # Events
        EVENT_ID = 'event_id'
        START_TIME = 'start_time'
        # Users
        DISPLAY_NAME = 'display_name'
        JOIN_TIME = 'join_time'

        # Properties name of the CaEvent and CaParticipants class
        # Events
        OUR_EVENT_ID = EVENT_ID
        OUR_START_TIME = START_TIME
        # Users
        OUR_DISPLAY_NAME = 'display_name'
        OUR_JOIN_TIME = 'timestamp'

        _ORDER_BY_KEY_MAPPING = {EVENT_ID: OUR_EVENT_ID,
                                 START_TIME: OUR_START_TIME,
                                 DISPLAY_NAME: OUR_DISPLAY_NAME,
                                 JOIN_TIME: OUR_JOIN_TIME}

        _our_user_args = None
        _user_original_args = None

        @property
        def value(self):
            return self._our_user_args

        @value.setter
        def value(self, values):
            def set_default_sorting_keys(values):
                if values is None:
                    values = tuple()

                if not any(usr_key in values
                           for usr_key in (self.EVENT_ID, self.START_TIME)):
                    log.debug('Adding default sorting value for event [%s]',
                              self.EVENT_ID)
                    values += (self.EVENT_ID,)

                if not any(usr_key in values
                           for usr_key in (self.DISPLAY_NAME, self.JOIN_TIME)):
                    log.debug('Adding default sorting value for user [%s]',
                              self.DISPLAY_NAME)
                    values += (self.DISPLAY_NAME,)
                return values

            values = set_default_sorting_keys(values)

            type(self)._user_original_args = values
            type(self)._our_user_args = self._map_fields(values)

        @property
        def event_sort_keys(self):
            """ Returns attrgetter to sort events by those attr. """
            event_properties_name_to_sort_by = tuple(
                k for k in self.value
                if k in (self.OUR_EVENT_ID, self.OUR_START_TIME)
            )
            return operator.attrgetter(*event_properties_name_to_sort_by)

        @property
        def participant_sort_keys(self):
            """ Returns attrgetter to sort participant by those attr. """
            participant_properties_name_to_sort_by = tuple(
                k for k in self.value
                if k in (self.OUR_DISPLAY_NAME, self.OUR_JOIN_TIME)
            )
            return operator.attrgetter(*participant_properties_name_to_sort_by)

        @classmethod
        def _map_fields(cls, values):
            """
            Translates form input args (from file, or cmd) to our properties
              on CaEvent and CaParticipants to sort by them.

            :param values:
            :return:
            """

            try:
                sorted_columns = OrderedDict(
                    ((cls._ORDER_BY_KEY_MAPPING[k], k) for k in values)
                )
            except KeyError as e:
                error_msg = ('Unrecognized order_by key, '
                             'got [{}]. Valid {}'.format(e, cls.choices))
                raise RuntimeError(error_msg) from None
            # Way of removing duplicates form list I could quickly think of
            return tuple(sorted_columns.keys())

        @ClassProperty
        @classmethod
        def choices(cls):
            return tuple(cls._ORDER_BY_KEY_MAPPING.keys())

    # Strings values, can be stored in user.cfg

    EVENT = _Option(
        'event',
        desc='Events ids to report')

    USER = _Option(
        'user',
        desc='Users ids to report')

    DATE_FROM = _Option(
        'date_from',
        desc='Include logs from this date and later [eg. "2016-07-02"]')

    DATE_TO = _Option(
        'date_to',
        desc='Exclude logs from this date and later [eg. "2016-07-03"]')

    ORDER_BY = _OrderByOpt(
        'order_by',
        # default='first_name',
        # TODO: Give 3 column names. Maybe all column names?
        desc='Order results by one of the column names: [3 column names]')

    # Connection settings
    COUCH_STRING = _Option(
        'couchdb_connection_string',
        default='http://127.0.0.1:5984/',
        desc='CouchDB connection string [Default: %(default)s]')

    COUCH_DATABASE = _Option(
        'couchdb_database',
        default='circleanywhere',
        desc='Database to be used by CouchDB [Default: %(default)s]')

    MONGO_STRING = _Option(
        'mongodb_connection_string',
        default='mongodb://127.0.0.1:27017',
        desc='MongoDB connection string [Default: %(default)s]')

    MONGO_DATABASE = _Option(
        'mongo_database',
        default='circleanywhere',
        desc='Database to be used by MongoDB [Default: %(default)s]')

    # Script options
    OUT_DEST = _Option(
        'output_destination',
        desc='File path to where the report should be saved [Default: screen]')

    CFG_PATH = _Option(
        'cfg',
        default='%s/ca_analytics.cfg',
        desc='Path to cfg file [Default: "%s/ca_analytics.cfg"]')

    LOG_PATH = _Option(
        'log',
        desc='Path to log file')

    # Program stuff
    # TODO: Get those as property
    _DB_MONGO = _Option(
        'db_mongo',
        desc='Reference to our mongoDB')

    _DB_COUCH = _Option(
        'db_couch',
        desc='Reference to our couchDB')

    _details_provider = _Option(
        'info_proxy',
        desc='Proxy to CouchDB from which we get detailed info about events '
             'and users.')

    @ClassProperty
    @classmethod
    def details_provider(cls):
        # TODO: Resolve somehow cyclic import. Move it to AppSetts?
        from lib.database import CaDetailsProvider
        if cls._details_provider.value is None:
            log.debug('Creating new CaDetailsProvider')
            cls._details_provider.value = CaDetailsProvider()

        return cls._details_provider.value

    @classmethod
    def get_config(cls, f_pth=''):
        """
        Get cfg dict from yaml file
        """
        try:
            f_pth = norm_path(f_pth, mkdir=False, mkfile=False, logger=log)
            with open(f_pth) as f:
                return yaml.load(f)
        except FileNotFoundError as e:
            log.debug(e)

    @ClassProperty
    @classmethod
    def opt_list(cls):
        def condition_to_be_opt(x):
            return x[0].isalpha() and x.isupper()

        return [Setts.__dict__[x] for x in Setts.__dict__ if
                condition_to_be_opt(x)]

    @ClassProperty
    @classmethod
    def cfg(cls):
        return {opt.key: opt.value for opt in cls.opt_list}

    @classmethod
    def refresh(cls, cfg=None, f_pth='', reset=False):
        """
        Refreshes app setts with yaml config file or cfg dict.
          Content of yaml cfg file will overwrite cfg dict!

        :version: 2017.01.12
        :version: 2016.12.03
        """
        if f_pth:
            log.debug('Loading (presumably) YAML file: "%s"', f_pth)
            cfg = cls.get_config(f_pth=f_pth)
        if not cfg:
            cfg = {}

        for opt in cls.opt_list:
            try:
                cfg_val = cfg.get(opt.key, None)
            except AttributeError:
                # Those are setts as ClassProperties for app use, so skip it
                continue

            if (cfg_val is None and opt.value is None) or reset:
                # When starting application
                opt.value = opt.default
            elif cfg_val is None:
                pass
            else:
                # When updating settings later
                opt.value = cfg_val


Setts.refresh()
