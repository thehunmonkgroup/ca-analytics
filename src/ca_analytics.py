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
import datetime
import collections
from os.path import join as j
from pymongo import MongoClient
from pprint import pprint, pformat

rwd = os.path.dirname(os.path.abspath(__file__))
if rwd not in sys.path:
    sys.path.append(rwd)

log = logging.getLogger()

try:
    from lib.extras import configure_argparse
except Exception as e:
    log.warning(e)


def main():
    args, parser = configure_argparse()
    print(parser.format_help())
    print('='*80)
    print(args)



version = {'y': 2016, 'm': 8, 'd': 7}
__version__ = '{y}.{m}.{d}'.format(**version)

if __name__ == '__main__':
    main()
