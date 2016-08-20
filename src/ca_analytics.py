#!/usr/bin/env python3
# (c) 2016 Alek
#  Exports Circle Anywhere analytical information

import logging
import os
import sys
from os.path import join as j
from pprint import pprint

import ruamel.yaml as yaml

from lib.db_engine import init_db
from lib.extras import configure_argparse, Setts, CaPrinter

rwd = os.path.dirname(os.path.abspath(__file__))
if rwd not in sys.path:
    sys.path.append(rwd)

log = logging.getLogger(__name__)


def evaluate_arguments(args):
    """
    eventId: 340, 342, 523

    :param args:
    :return:
    """

    events = Setts.DB_MONGO.value.get_events(event_ids=args.event)

    printer = CaPrinter(data=events)
    if args.output_destination:
        printer.write_file(f_path=args.output_destination)
    else:
        printer.write_terminal()


def main():
    # TODO: output: sort by user id or date users joined event?

    args, parser = configure_argparse(start_cmd=None)

    if args.sample:
        print('# Program defaults. Comment unnecessary')
        print(yaml.dump(Setts.cfg))
        sys.exit(0)

    # Load default cfg
    Setts.refresh(f_pth=j(rwd, Setts.CFG_PATH.value))
    # Load users cfg
    Setts.refresh(f_pth=args.cfg)
    # Load user args
    Setts.refresh(cfg=args.__dict__)
    init_db()
    evaluate_arguments(args)


version = {'y': 2016, 'm': 8, 'd': 18}
__version__ = '{y}.{m}.{d}'.format(**version)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.exception(e)
        sys.exit(1)
