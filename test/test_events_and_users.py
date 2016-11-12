#!/usr/bin/env python3
# (c) 2016 Alek
#  Integrations test for Circle Anywhere

import logging
import os
import sys
import unittest
from unittest.mock import patch

import ca_analytics
from ca_analytics import main
from example_data import ResponseFactory
from lib.db_engine import MongoData, CouchData

rwd = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
if rwd not in sys.path:
    sys.path.append(rwd)

log = logging.getLogger(__name__)


class TestMain(unittest.TestCase):
    # TODO: # Fail with: 00494, 00323: No event for id [00494] found in CouchDB

    @patch.object(ca_analytics, 'OutputHandler')
    @patch.object(CouchData, 'get_data',
                  side_effect=ResponseFactory.couch_get_data_side_effect)
    @patch.object(CouchData, '__init__', return_value=None)
    @patch.object(MongoData, 'get_data',
                  side_effect=ResponseFactory.mongo_get_data_side_effect)
    @patch.object(MongoData, '__init__', return_value=None)
    def test_should_select_all_users_attending_the_event(
            self, mock_mongo_init, mock_db_mongo, mock_coach_init,
            mock_coach_db, mock_output_handler):
        # Given
        cli_cmd = '-e 111'.split()

        # When
        main(start_cmd=cli_cmd)

        # Then
        # print(mock_mongo_init.call_args_list)
        # print(mock_db_mongo.call_args_list)
        # print(mock_coach_init.call_args_list)
        # print(mock_coach_db.call_args_list)
        # print(mock_output_handler.call_args_list)


if __name__ == '__main__':
    unittest.main()
