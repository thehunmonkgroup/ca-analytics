#!/usr/bin/env python3
# (c) 2016 Alek
#  Exports Circle Anywhere analytical information

import logging
import os
import sys
from os.path import join as j

from lib.database import init_db
from lib.engine import get_ca_event_list
from lib.extras import configure_argparse, Setts, OutputHandler

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

    # printer = OutputHandler(ca_events_list=event_list)
    # if Setts.OUT_DEST.value:
    #     printer.write_file(f_path=Setts.OUT_DEST.value)
    # else:
    #     printer.write_terminal()


def main(start_cmd=None):
    # start_cmd = '-h'.split()
    start_cmd = '--order_by eventId --order_by dateAndTime --order_by displayName'.split()
    # TODO: Check how it's behaving with yaml
    start_cmd = '--order_by eventId dateAndTime '.split()
    start_cmd = '-u 123 456'.split()
    args, parser = configure_argparse(rwd=rwd, start_cmd=start_cmd)
    # print(args)

    # Load default cfg
    Setts.refresh(f_pth=j(rwd, Setts.CFG_PATH.value))
    # Load users cfg
    Setts.refresh(f_pth=args.cfg)
    # Load user args
    Setts.refresh(cfg=args.__dict__)

    init_db()  # TODO: Must it be called?
    evaluate_arguments()


version = {'y': 2016, 'm': 12, 'd': 8}
__version__ = '{y}.{m}.{d}'.format(**version)

if __name__ == '__main__':
    # TODO: Decorator for properties, when _field is not None return earlier
    try:
        main()
    except Exception as e:
        log.exception(e)
        sys.exit(1)
