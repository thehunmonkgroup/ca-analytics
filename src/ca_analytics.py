#!/usr/bin/env python3
# (c) 2016 Alek
#  Exports Circle Anywhere analytical information

import logging
import os
import sys
from os.path import join as j

from lib.ca_engine import get_ca_events
from lib.db_engine import init_db
from lib.extras import configure_argparse, Setts, CaPrinter

rwd = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
if rwd not in sys.path:
    sys.path.append(rwd)

log = logging.getLogger(__name__)


def evaluate_arguments():
    db_data = Setts._DB_MONGO.value.get_data(event_ids=Setts.EVENT.value,
                                             user_ids=Setts.USER.value)
    db_data = Setts._DB_MONGO.value.filter_date(data=db_data,
                                                date_from=Setts.DATE_FROM.value,
                                                date_to=Setts.DATE_TO.value)

    ca_event_list = get_ca_events(db_data=db_data)
    # print('** aaa')
    # for line in ca_event_list:
    #     print(line)
    # print(line.event_users)
    # for x in line.event_users:
    #     print(x._mongo_raw_data)
    # pprint(line.user_list)

    # print('** bbb')
    printer = CaPrinter(ca_events_list=ca_event_list)
    if Setts.OUT_DEST.value:
        printer.write_file(f_path=Setts.OUT_DEST.value)
    else:
        printer.write_terminal()


def main(start_cmd=None):
    # start_cmd = ['-e', '389', '523',
    #              '-u', '116788992537476058951', '116964073935054089646', '100143115762434483634']
    # start_cmd = ['-e', '389', '523']
    # start_cmd = ['-e', '419']
    # start_cmd = ['-u', '116788992537476058951', '116964073935054089646']
    args, parser = configure_argparse(rwd=rwd, start_cmd=start_cmd)

    # Load default cfg
    Setts.refresh(f_pth=j(rwd, Setts.CFG_PATH.value))
    # Load users cfg
    Setts.refresh(f_pth=args.cfg)
    # Load user args
    Setts.refresh(cfg=args.__dict__)
    init_db()
    evaluate_arguments()


version = {'y': 2016, 'm': 11, 'd': 11}
__version__ = '{y}.{m}.{d}'.format(**version)

if __name__ == '__main__':
    try:
        # TODO: Add logging
        # TODO: docker CoachDB & MongoDB
        # TODO: Some test
        main()
    except Exception as e:
        log.exception(e)
        sys.exit(1)
