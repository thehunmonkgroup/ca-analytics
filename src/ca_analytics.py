#!/usr/bin/env python3
# (c) 2016 Alek
#  Exports Circle Anywhere analytical information

import logging
import os
import sys
from os.path import join as j

import ruamel.yaml as yaml

from lib.db_engine import init_db
from lib.extras import configure_argparse, Setts, CaPrinter

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
    printer = CaPrinter(data=db_data)
    if Setts.OUT_DEST.value:
        printer.write_file(f_path=Setts.OUT_DEST.value)
    else:
        printer.write_terminal()


def main():
    start_cmd = None
    args, parser = configure_argparse(rwd=rwd, start_cmd=start_cmd)
    if args.sample:
        print('# Program defaults. Comment unnecessary')
        print(yaml.dump(Setts.cfg), end='')
        sys.exit(0)

    # Load default cfg
    Setts.refresh(f_pth=j(rwd, Setts.CFG_PATH.value))
    # Load users cfg
    Setts.refresh(f_pth=args.cfg)
    # Load user args
    Setts.refresh(cfg=args.__dict__)
    init_db()
    evaluate_arguments()


version = {'y': 2016, 'm': 8, 'd': 20}
__version__ = '{y}.{m}.{d}'.format(**version)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.exception(e)
        sys.exit(1)
