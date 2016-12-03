#!/usr/bin/env python3
# (c) 2016 Alek
#  Exports Circle Anywhere analytical information

import logging
import os
import sys
from os.path import join as j
from pprint import pprint

from lib.engine import get_ca_event_list
from lib.database import init_db
from lib.extras import configure_argparse, Setts, OutputHandler, timeit

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

    event_list = get_ca_event_list(selected_logs=db_data)
    # pprint(event_list)

    # printer = OutputHandler(ca_events_list=ca_event_list)
    # if Setts.OUT_DEST.value:
    #     printer.write_file(f_path=Setts.OUT_DEST.value)
    # else:
    #     printer.write_terminal()


@timeit
def main(start_cmd=None):
    # start_cmd = '-u 109822325191351771849'.split()
    start_cmd = '-e 321 430'.split()
    # start_cmd = '-e 321 '.split()
    args, parser = configure_argparse(rwd=rwd, start_cmd=start_cmd)

    # Load default cfg
    Setts.refresh(f_pth=j(rwd, Setts.CFG_PATH.value))
    # Load users cfg
    Setts.refresh(f_pth=args.cfg)
    # Load user args
    Setts.refresh(cfg=args.__dict__)

    init_db()  # TODO: Must it be called?
    evaluate_arguments()


version = {'y': 2016, 'm': 12, 'd': 2}
__version__ = '{y}.{m}.{d}'.format(**version)

if __name__ == '__main__':
    try:
        # TODO: lib/engine.py:29
        main()
    except Exception as e:
        log.exception(e)
        sys.exit(1)
