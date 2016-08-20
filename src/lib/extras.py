#!/usr/bin/env python3
# (c) 2016 Alek
#  Exports Circle Anywhere analytical informations

import argparse
import collections
import errno
import logging
import os
from os.path import join as j

import ruamel.yaml as yaml

log = logging.getLogger(__name__)


class CaPrinter:
    _data = None
    _lines = None
    _sep = '-' * 25

    def __init__(self, data):
        """
        Here is raw data. During printing/writing to file it's converted in
        `_prepare_output`.:

        :param data: json list/db_cursor
            {'eventId': 286, 'message': 'events', 'connectedUsers': 0, 'timestamp': '2016-03-19T03:27:14.150Z', 'userId': '112349864121259291250', 'level': 'info', '_id': ObjectId('57a3a39600c88030ca3faf88'), 'action': 'join'}
            {'eventId': 286, 'message': 'events', 'connectedUsers': 1, 'timestamp': '2016-03-19T03:27:27.177Z', 'userId': '116488113102013485647', 'level': 'info', '_id': ObjectId('57a3a39600c88030ca3faf98'), 'action': 'join'}
            {'eventId': 266, 'message': 'events', 'connectedUsers': 0, 'timestamp': '2016-03-19T04:38:34.221Z', 'userId': '114498861474704307604', 'level': 'info', '_id': ObjectId('57a3a39600c88030ca3fb10e'), 'action': 'join'}
            {'eventId': 292, 'message': 'events', 'connectedUsers': 1, 'timestamp': '2016-03-19T08:59:37.600Z', 'userId': '108611793445678484173', 'level': 'info', '_id': ObjectId('57a3a39600c88030ca3fb3cc'), 'action'
        """
        self._data = data

    @property
    def lines(self):
        """
        List of lines to ber written to output.
        """
        if self._lines is None:
            self._lines = self._prepare_output()
        return self._lines

    def _prepare_output(self):
        out = []
        tmp = collections.defaultdict(dict)

        for line in self._data:
            tmp[line['eventId']][line['userId']] = line['timestamp']

        for event_id, users in sorted(tmp.items()):
            out.append(self._sep)
            out.append("Event ID: %s" % event_id)
            for user_id, timestamp in sorted(users.items(),
                                             key=lambda x: x[0]):
                out.append("    %s: %s" % (user_id, timestamp))
            out.append(self._sep)
        return out

    def write_terminal(self):
        for line in self.lines:
            print(line)

    def write_file(self, f_path):
        with open(f_path, 'w') as f:
            print('* Writing to file: "%s"' % f_path)
            f.write('\n'.join(self.lines))
            print('* Done')


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


def configure_argparse(start_cmd=None):
    """
    :return
    Namespace(
        cfg=None,
        couchdb_connection_string=None,
        couchdb_database=None,
        end_date=None,
        event=None,
        log=None,
        mongo_database=None,
        mongodb_connection_string=None,
        output_destination=None,
        sample=False,
        start_date=None,
        user=None
    )
    """

    parser = argparse.ArgumentParser(
        description='Exports Circle Anywhere analytical information',
        add_help=False,
        usage='%(prog)s [-e [EVENT_ID [EVENT_ID ...]]] [-u [USER_ID [USER_ID ...]]] [--start-date DATE] [--end_date DATE] [CONFIGURATION]'
    )

    stats_opt = parser.add_argument_group('Analytics Options')

    stats_opt.add_argument('-e', '--' + Setts.EVENT.key,
                           # default=Setts.EVENT.default,
                           help=Setts.EVENT.desc,
                           metavar='EVENT_ID',
                           type=int,
                           nargs='*',
                           )

    stats_opt.add_argument('-u', '--' + Setts.USER.key,
                           # default=Setts.USER.default,
                           help=Setts.USER.desc,
                           metavar='USER_ID',
                           type=int,
                           nargs='*',
                           )

    stats_opt.add_argument('--' + Setts.START_DATE.key,
                           # default=Setts.START_DATE.default,
                           help=Setts.START_DATE.desc,
                           metavar='DATE',
                           type=str,
                           )

    stats_opt.add_argument('--' + Setts.END_DATE.key,
                           # default=Setts.END_DATE.default,
                           help=Setts.END_DATE.desc,
                           metavar='DATE',
                           type=str,
                           )

    conn_opt = parser.add_argument_group('Connection Options')

    conn_opt.add_argument('--' + Setts.COUCH_STRING.key,
                          type=str,
                          # default=Setts.COUCH_STRING.default,
                          help=Setts.COUCH_STRING.desc,
                          metavar='URL',
                          )

    conn_opt.add_argument('--' + Setts.COUCH_DATABASE.key,
                          type=str,
                          # default=Setts.COUCH_DATABASE.default,
                          help=Setts.COUCH_DATABASE.desc,
                          metavar='NAME',
                          )

    conn_opt.add_argument('--' + Setts.MONGO_STRING.key,
                          type=str,
                          # default=Setts.MONGO_STRING.default,
                          help=Setts.MONGO_STRING.desc,
                          metavar='URI',
                          )

    conn_opt.add_argument('--' + Setts.MONGO_DATABASE.key,
                          type=str,
                          # default=Setts.MONGO_DATABASE.default,
                          help=Setts.MONGO_DATABASE.desc,
                          metavar='NAME',
                          )

    conf_opt = parser.add_argument_group('Configuration')

    conf_opt.add_argument('-o', '--' + Setts.OUT_DEST.key,
                          type=str,
                          # default=Setts.OUT_DEST.default,
                          help=Setts.OUT_DEST.desc,
                          metavar='FILE',
                          )

    conf_opt.add_argument('-c', '--' + Setts.CFG_PATH.key,
                          type=str,
                          # dest='cfg',
                          # default=Setts.CFG_PATH.default,
                          help=Setts.CFG_PATH.desc,
                          metavar='FILE',
                          )

    conf_opt.add_argument('--sample',
                          action='store_true',
                          help='Print sample YAML config file',
                          # metavar='FILE',
                          )

    conf_opt.add_argument('-l', '--' + Setts.LOG_PATH.key,
                          type=str,
                          # default=Setts.LOG_PATH.default,
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


class Setts:
    # If args are validated, the default option should always be set
    class Option:
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
            return 'Option(key=%s, ' \
                   'value=%s, ' \
                   'default=%s, ' \
                   'desc="%s", ' \
                   'callback=%s)' % (self.key, self.value, self.default,
                                     self.desc, self.callback)

        def __str__(self):
            return '"%s": "%s"' % (self.key, self.value)

    class ClassProperty(property):
        def __get__(self, cls, owner):
            return self.fget.__get__(None, owner)()

    # _cfg = {}
    # Strings values, can be stored in user.cfg

    EVENT = Option(
        'event',
        default=[],
        desc='Events ids to report')

    USER = Option(
        'user',
        default=[],
        desc='Users ids to report')

    START_DATE = Option(
        'start_date',
        default='',
        desc='Give starting date from which to report')

    END_DATE = Option(
        'end_date',
        default='',
        desc="The lower bound for the report's date")

    # Connection settings
    COUCH_STRING = Option(
        'couchdb_connection_string',
        default='http://127.0.0.1:5984/',
        desc='CouchDB connection string [Default: %(default)s]')

    COUCH_DATABASE = Option(
        'couchdb_database',
        default='circleanywhere',
        desc='Database to be used by CouchDB [Default: %(default)s]')

    MONGO_STRING = Option(
        'mongodb_connection_string',
        default='mongodb://127.0.0.1:27017',
        desc='MongoDB connection string [Default: %(default)s]')

    MONGO_DATABASE = Option(
        'mongo_database',
        default='circleanywhere',
        desc='Database to be used by MongoDB [Default: %(default)s]')

    # Script options
    OUT_DEST = Option(
        'output_destination',
        default='',
        desc='File path to where the report should be saved [Default: screen]')

    CFG_PATH = Option(
        'cfg',
        default='ca_analytics.cfg',
        desc='Path to cfg file [Default: "$(pwd)/%(default)s"]')

    LOG_PATH = Option(
        'log',
        default='',
        desc='Path to log file')

    # Program stuff
    DB_MONGO = Option(
        'db_mongo',
        desc='Reference to our mongoDB')

    DB_COUCH = Option(
        'db_couch',
        desc='Reference to our couchDB')

    @classmethod
    def get_config(cls, f_pth=''):
        """
        Get cfg dict from yaml file
        """
        try:
            with open(f_pth) as f:
                return yaml.load(f)
        except FileNotFoundError as e:
            log.debug(e)

    @ClassProperty
    @classmethod
    def opt_list(cls):
        def condition_to_be_opt(x):
            return x[0].isalpha() and x.isupper()

        # return {x: Setts.__dict__[x] for x in Setts.__dict__ if
        #                                                 condition_to_be_opt(x)}
        return [Setts.__dict__[x] for x in Setts.__dict__ if
                condition_to_be_opt(x)]

    @ClassProperty
    @classmethod
    def cfg(cls):
        return {opt.key: opt.value for opt in cls.opt_list}

    @classmethod
    def refresh(cls, cfg=None, f_pth=''):
        """
        Refreshes app setts with yaml config file or cfg dict.
          Content of yaml cfg file will overwrite cfg dict!

        :version: 2016.08.17
        """
        if f_pth:
            log.debug('Loading (presumably) YAML file: "%s"', f_pth)
            cfg = cls.get_config(f_pth=f_pth)
        if not cfg:
            cfg = {}

        for opt in cls.opt_list:
            cfg_val = cfg.get(opt.key, None)

            if cfg_val is None and opt.value is None:
                # Start
                opt.value = opt.default
            elif cfg_val is None:
                pass
            else:
                opt.value = cfg_val


Setts.refresh()
