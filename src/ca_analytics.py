#!/usr/bin/env python3
# (c) 2016 Alek
#  Exports Circle Anywhere analytical information

import logging
import os
import sys
from os.path import join as j
from pprint import pprint

from lib.ca_engine import get_ca_events
from lib.db_engine import init_db
from lib.extras import configure_argparse, Setts

rwd = os.path.dirname(os.path.abspath(__file__))
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

    for line in ca_event_list:
        print(line)
        pprint(line.user_list)

        # printer = CaPrinter(data=db_data)
        # if Setts.OUT_DEST.value:
        #     printer.write_file(f_path=Setts.OUT_DEST.value)
        # else:
        #     printer.write_terminal()


def main():
    start_cmd = ['-e', '389', '523']
    args, parser = configure_argparse(rwd=rwd, start_cmd=start_cmd)

    # Load default cfg
    Setts.refresh(f_pth=j(rwd, Setts.CFG_PATH.value))
    # Load users cfg
    Setts.refresh(f_pth=args.cfg)
    # Load user args
    Setts.refresh(cfg=args.__dict__)
    init_db()
    evaluate_arguments()


version = {'y': 2016, 'm': 11, 'd': 6}
__version__ = '{y}.{m}.{d}'.format(**version)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.exception(e)
        sys.exit(1)
