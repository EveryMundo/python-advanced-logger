import json
import logging
import unittest

from advanced_logger import register_logger, initialize_logger_settings, clear_all_loggers
from advanced_logger.advanced_logger import set_global_log_level

__author__ = 'neil@everymundo.com'


class AdvancedLoggingTracebackTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(AdvancedLoggingTracebackTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(AdvancedLoggingTracebackTestCase, cls).tearDownClass()

    def setUp(self):
        clear_all_loggers()
        set_global_log_level(logging.INFO)
        super(AdvancedLoggingTracebackTestCase, self).setUp()

    def tearDown(self):
        super(AdvancedLoggingTracebackTestCase, self).tearDown()

    def test_traceback_logging(self):
        """
        Leave this test as the first one, because there are some sections dependent on line number
        and adding to the beginning of this file would mean modifying this test to update the line numbers
        """
        test_cases = ['exception', 'log_exception_info']
        for test_case in test_cases:
            initialize_logger_settings(project_dir_name='advanced_logger')
            test_logger = register_logger('test_logger')

            # noinspection PyUnresolvedReferences
            def nested_foo():
                foo()

            # noinspection PyUnresolvedReferences
            def double_nested_foo():
                try:
                    foo()
                except Exception:
                    nested_foo()

            try:
                returned_obj = None
                double_nested_foo()
            except NameError as e:
                if test_case == 'exception':
                    returned_obj = test_logger.exception(
                        e, msg='testing logging', return_it=True, log_it=False
                    )
                elif test_case == 'log_exception_info':
                    returned_obj = test_logger.log_exception_info(
                        e, msg='testing logging', return_it=True, log_it=False
                    )
                else:
                    self.fail('added testcase without expanding tests')

            self.assertIsNotNone(returned_obj)

            expected_return = {
                'e': "name 'foo' is not defined",
                'msg': 'testing logging',
                'traceback': [
                    'Traceback (most recent call last):',
                    [
                        [
                            'advanced_logger.tests.test_traceback_logging.py',
                            'line 45',
                            'double_nested_foo'
                        ],
                        '    foo()',
                    ],
                    "NameError: name 'foo' is not defined",
                    'During handling of the above exception, another exception occurred:',
                    [
                        'Traceback (most recent call last):',
                        [
                            [
                                'advanced_logger.tests.test_traceback_logging.py',
                                'line 51',
                                'test_traceback_logging'
                            ],
                            '    double_nested_foo()'
                        ],
                        [
                            [
                                'advanced_logger.tests.test_traceback_logging.py',
                                'line 47',
                                'double_nested_foo'
                            ],
                            '    nested_foo()',
                        ],
                        [
                            [
                                'advanced_logger.tests.test_traceback_logging.py',
                                'line 40',
                                'nested_foo'
                            ],
                            '    foo()',
                        ],
                        "NameError: name 'foo' is not defined"
                    ],
                ]
            }

            self.assertEqual(
                expected_return,
                returned_obj,
                msg=json.dumps(returned_obj, indent=4)
            )

