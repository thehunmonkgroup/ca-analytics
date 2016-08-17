#!/usr/bin/env python3
# (c) 2016 Alek
#  Exports Circle Anywhere analytical information

import os
import re
import sys
import json
import time
import couchdb
import logging
import ruamel.yaml as yaml
import datetime
import collections
from os.path import join as j
from pymongo import MongoClient
from pprint import pprint, pformat

rwd = os.path.dirname(os.path.abspath(__file__))
if rwd not in sys.path:
    sys.path.append(rwd)

log = logging.getLogger(__name__)

try:
    from lib.extras import configure_argparse, Setts
except Exception as e:
    log.warning(e)


def main():
    args, parser = configure_argparse(start_cmd='-e 345 5467 --cfg /some/path --couchdb_connection_string some:conn-string.wx'.split())

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
    print(args)
    pprint(Setts.cfg)


version = {'y': 2016, 'm': 8, 'd': 17}
__version__ = '{y}.{m}.{d}'.format(**version)

if __name__ == '__main__':
    main()
