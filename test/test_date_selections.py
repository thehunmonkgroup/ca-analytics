import logging
import os
import sys
from unittest import TestCase
from unittest.mock import patch

import dateutil.parser

import ca_analytics
from ca_analytics import main
from example_data import User_2016_07_02
from helpers import DbPatcherMixin
from lib.database import MongoData

rwd = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
if rwd not in sys.path:
    sys.path.append(rwd)

log = logging.getLogger(__name__)


class TestDateFilter(DbPatcherMixin, TestCase):
    DATE_TEST_USER_ID = User_2016_07_02.userId
    CMD_TEST_DATE = '-u %s ' % DATE_TEST_USER_ID

    def setUp(self):
        self.patcher_get_ca_event_list = patch.object(ca_analytics,
                                                      'get_ca_event_list')
        # Start patch
        self.mock_get_ca_event_list = self.patcher_get_ca_event_list.start()
        super().setUp()

    def test_should_filter_out_earlier_dates(self):
        # GIVEN
        expected_date_from = '2016-07-02'
        cmd = self.CMD_TEST_DATE + '--date_from %s' % expected_date_from
        cmd = cmd.split()

        # WHEN
        main(start_cmd=cmd)

        # THEN
        filtered_logs = self.get_filtered_mongo_data()
        self.check_if_dates_later_or_equal_than(date_from=expected_date_from,
                                                logs=filtered_logs)

    def test_should_filter_out_later_or_equal_dates(self):
        # GIVEN
        expected_date_to = '2016-07-02'
        cmd = self.CMD_TEST_DATE + '--date_to %s' % expected_date_to
        cmd = cmd.split()

        # WHEN
        main(start_cmd=cmd)

        # THEN
        filtered_logs = self.get_filtered_mongo_data()
        self.check_if_dates_earlier_than(date_to=expected_date_to,
                                         logs=filtered_logs)

    def test_should_include_up_but_not_low_bound_when_period_given(self):
        # GIVEN
        expected_date_from = '2016-07-02'
        expected_date_to = '2016-07-05'
        cmd = (
            self.CMD_TEST_DATE + '--date_from %s --date_to %s'
            % (expected_date_from, expected_date_to)
        )
        cmd = cmd.split()

        # WHEN
        main(start_cmd=cmd)

        # THEN
        filtered_logs = self.get_filtered_mongo_data()

        self.check_if_dates_later_or_equal_than(date_from=expected_date_from,
                                                logs=filtered_logs)
        self.check_if_dates_earlier_than(date_to=expected_date_to,
                                         logs=filtered_logs)

    def get_filtered_mongo_data(self):
        """
        This is returned after filtering
        :return:
        """
        db_data = self.mock_get_ca_event_list.call_args[1]['selected_logs']
        return db_data

    def check_if_dates_earlier_than(self, date_to, logs):
        date_to = self._parse_cmd_date(cmd_date=date_to)

        for row in logs:
            log_date = dateutil.parser.parse(row['timestamp'])
            self.assertGreater(date_to, log_date)

    def check_if_dates_later_or_equal_than(self, date_from, logs):
        date_from = self._parse_cmd_date(cmd_date=date_from)

        for row in logs:
            log_date = dateutil.parser.parse(row['timestamp'])
            self.assertLessEqual(date_from, log_date)

    @classmethod
    def _parse_cmd_date(cls, cmd_date):
        # TODO: Change _TIME_TEMPLATE to not be private
        str_date = MongoData._TIME_TEMPLATE % cmd_date
        parsed_date = dateutil.parser.parse(str_date)
        return parsed_date
