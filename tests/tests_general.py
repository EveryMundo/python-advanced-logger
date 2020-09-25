import json
import logging
import os
import re
import unittest
from unittest.mock import Mock

from advanced_logger import register_logger, initialize_logger_settings, deregister_logger, clear_all_loggers
from advanced_logger.advanced_logger import _format_traceback_line, __log__, set_global_log_level

__author__ = 'neil@everymundo.com'


# noinspection DuplicatedCode
class AdvancedLoggingGeneralTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(AdvancedLoggingGeneralTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(AdvancedLoggingGeneralTestCase, cls).tearDownClass()

    def setUp(self):
        clear_all_loggers()
        set_global_log_level(logging.INFO)
        super(AdvancedLoggingGeneralTestCase, self).setUp()

    def tearDown(self):
        super(AdvancedLoggingGeneralTestCase, self).tearDown()

    def test_format_traceback_line_doesnt_affect_line_without_path(self):
        # sanity check on regular line without a path
        test_str = 'one{0}two{0}three{0}four'.format(os.path.sep)

        formatted_line, is_chained = _format_traceback_line(test_str)
        self.assertEqual(formatted_line, [test_str])
        self.assertEqual(is_chained, False)

    def test_format_traceback_line_project_name(self):
        test_str = 'File "foo{0}bar{0}Blah{0}blah{0}test.foo", line 1, in two{0}three{0}four'.format(os.path.sep)

        initialize_logger_settings(project_dir_name=None)
        formatted_line, is_chained = _format_traceback_line(test_str)
        self.assertEqual([[['File "foo.bar.Blah.blah.test.foo', 'line 1', 'two.three.four']]], formatted_line)

        initialize_logger_settings(project_dir_name='bad project name test')
        formatted_line, is_chained = _format_traceback_line(test_str)
        self.assertEqual([[['File "foo.bar.Blah.blah.test.foo', 'line 1', 'two.three.four']]], formatted_line)

        initialize_logger_settings(project_dir_name="blah")
        formatted_line, is_chained = _format_traceback_line(test_str)
        self.assertEqual([[['blah.test.foo', 'line 1', 'two.three.four']]], formatted_line)

    def test_format_traceback_line_file_line_not_match_format(self):
        test_str = 'File test string lalala'
        formatted_line, is_chained = _format_traceback_line(test_str)
        self.assertEqual(['no match for exception formatter, showing raw input', test_str, test_str], formatted_line)

    def test_random_chance(self):
        test_logger = register_logger('test_logger')
        yes_test = test_logger.info(msg='This should log', return_it=True, log_it=False, likelihood=100, out_of=100)
        self.assertIsNotNone(yes_test)
        no_test = test_logger.info(msg='This should not log', return_it=True, log_it=False, likelihood=0, out_of=100)
        self.assertIsNone(no_test)
        no_test = test_logger.exception(msg='This should not log', return_it=True, log_it=False, likelihood=0, out_of=100)
        self.assertIsNone(no_test)

    def test_debug_hook(self):
        mock_test_hook = Mock()

        initialize_logger_settings(debug_hook_fn=mock_test_hook, global_log_level=logging.DEBUG)
        test_logger = register_logger('test')
        test_logger.debug('foo')
        test_logger.info('foo')

        self.assertEqual(mock_test_hook.call_count, 1)
        mock_test_hook.assert_called_once_with('foo')
        mock_test_hook.reset_mock()

        initialize_logger_settings(reset_values_if_not_argument=True, update_existing=True)
        test_logger.debug('foo')
        test_logger.info('foo')
        self.assertEqual(mock_test_hook.call_count, 0)

    def test_testing_hook(self):
        mock_test_hook = Mock()

        initialize_logger_settings(testing_hook_fn=mock_test_hook, reset_values_if_not_argument=True)
        test_logger = register_logger('test')
        test_logger.info('foo')
        self.assertEqual(mock_test_hook.call_count, 0)

        initialize_logger_settings(is_testing_fn=True, update_existing=True)
        test_logger = register_logger('test')
        test_logger.info('foo')
        self.assertEqual(mock_test_hook.call_count, 1)
        mock_test_hook.assert_called_once_with('foo')
        mock_test_hook.reset_mock()

        initialize_logger_settings(reset_values_if_not_argument=True, update_existing=True)
        test_logger.info('foo')
        self.assertEqual(mock_test_hook.call_count, 0)

    def test_log_levels(self):
        set_global_log_level(logging.CRITICAL)
        test_logger = register_logger('test_logger')
        self.assertIsNone(test_logger.debug('test', return_it=True, log_it=False))
        self.assertIsNone(test_logger.info('test', return_it=True, log_it=False))
        self.assertIsNone(test_logger.warn('test', return_it=True, log_it=False))
        self.assertIsNone(test_logger.error('test', return_it=True, log_it=False))
        self.assertIsNotNone(test_logger.critical('test', return_it=True, log_it=False))
        self.assertIsNotNone(test_logger.exception('e', return_it=True, log_it=False))
        self.assertIsNotNone(test_logger.exception(e=None, msg='e', return_it=True, log_it=False))
        self.assertIsNotNone(test_logger.log_exception_info(e=None, msg='e', return_it=True, log_it=False))
        test_logger.setLevel(logging.DEBUG)
        self.assertIsNotNone(test_logger.debug('test', return_it=True, log_it=False))
        self.assertIsNotNone(test_logger.info('test', return_it=True, log_it=False))
        self.assertIsNotNone(test_logger.warn('test', return_it=True, log_it=False))
        self.assertIsNotNone(test_logger.error('test', return_it=True, log_it=False))
        self.assertIsNotNone(test_logger.critical('test', return_it=True, log_it=False))
        self.assertIsNotNone(test_logger.exception('e', return_it=True, log_it=False))
        self.assertIsNotNone(test_logger.exception(e=None, msg='e', return_it=True, log_it=False))
        self.assertIsNotNone(test_logger.log_exception_info(e=None, msg='e', return_it=True, log_it=False))
        test_logger.disabled = True
        self.assertIsNone(test_logger.debug('test', return_it=True, log_it=False))
        self.assertIsNone(test_logger.log_exception_info(e=None, msg='e', return_it=True, log_it=False))

    def test_set_global_log_level(self):
        set_global_log_level(logging.WARNING)
        test_logger1 = register_logger('test_logger1')

        logged = test_logger1.log(logging.DEBUG, return_it=True, log_it=False, msg='lalala')
        self.assertIsNone(logged)

        logged = test_logger1.log(logging.WARNING, return_it=True, log_it=False, msg='lalala')
        logged = json.loads(logged)
        del logged['meta']['time']
        test_compare_log_obj = {'meta': {'name': test_logger1.name, 'level': 'WARNING'}, 'msg': 'lalala'}
        self.assertEqual(test_compare_log_obj, logged)

        #
        set_global_log_level(logging.INFO, update_existing=True)
        logged = test_logger1.log(logging.INFO, return_it=True, log_it=False, msg='lalala')
        logged = json.loads(logged)
        del logged['meta']['time']
        test_compare_log_obj = {'meta': {'name': test_logger1.name, 'level': 'INFO'}, 'msg': 'lalala'}
        self.assertEqual(test_compare_log_obj, logged)

        test_logger2 = register_logger('test_logger2')
        logged = test_logger2.log(logging.INFO, return_it=True, log_it=False, msg='lalala')
        logged = json.loads(logged)
        del logged['meta']['time']
        test_compare_log_obj = {'meta': {'name': test_logger2.name, 'level': 'INFO'}, 'msg': 'lalala'}
        self.assertEqual(test_compare_log_obj, logged)

        #
        set_global_log_level(logging.DEBUG, update_existing=False)
        test_logger3 = register_logger('test_logger3')
        logged = test_logger3.log(logging.DEBUG, return_it=True, log_it=False, msg='lalala')
        logged = json.loads(logged)
        del logged['meta']['time']
        test_compare_log_obj = {'meta': {'name': test_logger3.name, 'level': 'DEBUG'}, 'msg': 'lalala'}
        self.assertEqual(test_compare_log_obj, logged)

        logged = test_logger1.log(logging.DEBUG, return_it=True, log_it=False, msg='lalala')
        self.assertIsNone(logged)

    def test_register_deregister(self):
        test_logger1 = register_logger('test_logger')
        self.assertEqual(test_logger1.disabled, False)

        deregister_logger(test_logger1)
        self.assertEqual(test_logger1.disabled, True)

        test_logger1a = register_logger('test_logger')
        self.assertEqual(test_logger1a.disabled, False)
        self.assertIsNot(test_logger1, test_logger1a)

    def test_deregister(self):
        test_logger1 = register_logger('test1')
        test_logger2 = register_logger('test2')
        test_logger3 = register_logger('test3')
        test_logger4 = register_logger('test4')
        test_logger5 = register_logger('test5')
        from advanced_logger.advanced_logger import _registered_loggers

        self.assertEqual(len(_registered_loggers), 5)

        test_logger1.deregister()
        self.assertEqual(len(_registered_loggers), 4)
        self.assertEqual(test_logger1.disabled, True)

        deregister_logger(test_logger2)
        self.assertEqual(len(_registered_loggers), 3)
        self.assertEqual(test_logger2.disabled, True)

        deregister_logger('test3')
        self.assertEqual(len(_registered_loggers), 2)
        self.assertEqual(test_logger3.disabled, True)
        self.assertEqual(test_logger4.disabled, False)

        clear_all_loggers()
        self.assertEqual(len(_registered_loggers), 0)
        self.assertEqual(test_logger4.disabled, True)
        self.assertEqual(test_logger5.disabled, True)

        register_logger('test1')
        register_logger('test2')
        register_logger('test3')
        register_logger('foobar3')
        register_logger('foobar4')
        register_logger('leftover')
        self.assertEqual(len(_registered_loggers), 6)
        clear_all_loggers(exact_filter='test')
        self.assertEqual(len(_registered_loggers), 6)
        clear_all_loggers(exact_filter='test3')
        self.assertEqual(len(_registered_loggers), 5)
        clear_all_loggers(substr_filter='test')
        self.assertEqual(len(_registered_loggers), 3)
        clear_all_loggers(regex_filter=re.compile('^foobar'))
        self.assertEqual(len(_registered_loggers), 1)
        clear_all_loggers()
        self.assertEqual(len(_registered_loggers), 0)

    def test_logger_prefix(self):
        initialize_logger_settings(global_log_name_prefix='TEST_PREFIX')
        test_logger = register_logger('test_logger')
        self.assertEqual('TEST_PREFIXtest_logger', test_logger.name)

        initialize_logger_settings(global_log_name_prefix='TEST_PREFIX2')
        test_logger = register_logger('test_logger')
        self.assertEqual('TEST_PREFIX2test_logger', test_logger.name)

    def test_log_it(self):
        # actually test logging something, as all the other tests have been using log_it=False, return_it=True
        test_logger = register_logger('test_logger', logging.DEBUG)
        self.assertIsNotNone(test_logger.debug('Testing logger output to stdout case 1', return_it=True, log_it=True))
        self.assertIsNone(test_logger.debug('Testing logger output to stdout case 2', return_it=False, log_it=True))
        self.assertIsNone(test_logger.debug('Testing logger output to stdout case 3'))
        self.assertIsNone(test_logger.exception('Testing logger output to stdout case 3'))
        self.assertIsNone(test_logger.exception('Testing logger output to stdout case 3', indent=2))

    # def test_basic_config(self):
    #     Should fully test this eventually
    #     self.fail()
    #
    # def test_initialize_settings(self):
    #     Should fully test this eventually
    #     self.fail()
