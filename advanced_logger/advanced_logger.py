import os
import re
import sys
import random
import traceback
import json
import logging
from datetime import datetime
from logging import Logger as BaseLogger
from typing import Optional, Dict, Union, List, Callable, TextIO
from typing.io import IO

from advanced_logger.json_encoder.advanced_json_encoder import RE_TYPE, AdvancedJSONEncoder

__author__ = 'neil@everymundo.com'


#

def _default_is_testing_fn():
    return False


_GLOBAL_LOG_LEVEL = logging.DEBUG
_LOG_STREAM_DESTINATION = sys.stdout
_LOG_FILE_DESTINATION = None

_registered_loggers = set()

_PROJECT_DIR_NAME: Optional[str] = None
_PREFIX = ""
_IS_TESTING = _default_is_testing_fn
_TESTING_HOOK = None
_DEBUG_HOOK = None
_AdvancedJSONEncoder = AdvancedJSONEncoder  # TODO, swappable
_CURRENT_BASE_LOGGER_CLASS = logging.Logger

_LOGGER_OUTPUT_TYPE = Union[str, List, '_LOGGER_OUTPUT_TYPE']


class AdvancedLogger(BaseLogger):
    def __init__(self, name: str, level: int = None, testing_hook_fn: Callable = None, debug_hook_fn: Callable = None):
        """
        Initialize the logger with a name and an optional level.
        """
        if level is None:
            level = _GLOBAL_LOG_LEVEL
        self.testing_hook = testing_hook_fn or _TESTING_HOOK
        self.debug_hook = debug_hook_fn or _DEBUG_HOOK

        super(AdvancedLogger, self).__init__(name, level)

    def debug(self, msg, *args, **kwargs) -> Optional[str]:
        if self.isEnabledFor(logging.DEBUG):
            if self.debug_hook:
                self.debug_hook(msg, *args, **kwargs)
            return self.log(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs) -> Optional[str]:
        if self.isEnabledFor(logging.INFO):
            return self.log(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs) -> Optional[str]:
        if self.isEnabledFor(logging.WARNING):
            return self.log(logging.WARNING, msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs) -> Optional[str]:
        return self.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs) -> Optional[str]:
        if self.isEnabledFor(logging.ERROR):
            return self.log(logging.ERROR, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs) -> Optional[str]:
        if self.isEnabledFor(logging.CRITICAL):
            return self.log(logging.CRITICAL, msg, *args, **kwargs)

    def log_exception_info(self, e: Exception = None, *args, msg: str = None, **kwargs) -> Optional[Dict]:
        # legacy name from when this was an internal library
        return _log_exception_info(self, e=e, *args, msg=msg, **kwargs)

    def exception(self, e: Exception = None, *args, msg: str = None, **kwargs) -> Optional[Dict]:
        return _log_exception_info(self, e=e, *args, msg=msg, **kwargs)

    def log(self, level, msg, *args, **kwargs) -> Optional[str]:
        if self.testing_hook and _IS_TESTING and _IS_TESTING():
            self.testing_hook(msg, *args, **kwargs)
        return __log__(self, level, msg, *args, **kwargs)

    def deregister(self):
        deregister_logger(self)


def initialize_logger_settings(
        *,
        global_log_level=None,
        global_log_name_prefix=None,
        project_dir_name: str = None,
        # python_dir_path: str = None,
        log_stream_destination: TextIO = None,
        log_file_destination: IO = None,
        is_testing_fn: Union[Callable, bool] = None,
        testing_hook_fn: Callable = None,
        debug_hook_fn: Callable = None,
        reset_values_if_not_argument=False,
        update_existing=False,
        base_logger_class=None,
):
    global _LOG_STREAM_DESTINATION, _LOG_FILE_DESTINATION, _PREFIX, _PROJECT_DIR_NAME, \
        _IS_TESTING, _TESTING_HOOK, _DEBUG_HOOK, _CURRENT_BASE_LOGGER_CLASS

    if log_stream_destination is not None or reset_values_if_not_argument:
        _LOG_STREAM_DESTINATION = log_stream_destination
    if log_file_destination is not None or reset_values_if_not_argument:
        _LOG_FILE_DESTINATION = log_file_destination
    if global_log_level is not None or reset_values_if_not_argument:
        if global_log_level is None:
            global_log_level = logging.INFO
        set_global_log_level(global_log_level, update_existing=False)
    if global_log_name_prefix is not None or reset_values_if_not_argument:
        _PREFIX = global_log_name_prefix or ''
    if project_dir_name is not None or reset_values_if_not_argument:
        _PROJECT_DIR_NAME = project_dir_name
    if testing_hook_fn is not None or reset_values_if_not_argument:
        _TESTING_HOOK = testing_hook_fn
        if update_existing:
            for rl in _registered_loggers:  # type: AdvancedLogger
                rl.testing_hook = _TESTING_HOOK
    if debug_hook_fn is not None or reset_values_if_not_argument:
        _DEBUG_HOOK = debug_hook_fn
        if update_existing:
            for rl in _registered_loggers:  # type: AdvancedLogger
                rl.debug_hook = _DEBUG_HOOK
    if is_testing_fn is not None or reset_values_if_not_argument:
        if isinstance(is_testing_fn, bool):
            def testing_fn_return_bool() -> bool:
                return is_testing_fn

            _IS_TESTING = testing_fn_return_bool
        elif is_testing_fn is None:
            _IS_TESTING = _default_is_testing_fn()
        else:
            _IS_TESTING = is_testing_fn
    if base_logger_class is not None or reset_values_if_not_argument:
        if base_logger_class is None:
            base_logger_class = logging.Logger
        _CURRENT_BASE_LOGGER_CLASS = base_logger_class

    logging.setLoggerClass(AdvancedLogger)
    basic_config()


def basic_config(**kwargs):
    if 'project_dir_name' in kwargs:
        global _PROJECT_DIR_NAME
        _PROJECT_DIR_NAME = kwargs['project_dir_name']
    if 'stream' not in kwargs and _LOG_STREAM_DESTINATION:
        kwargs['stream'] = _LOG_STREAM_DESTINATION
    if 'filename' not in kwargs and _LOG_FILE_DESTINATION:
        kwargs['filename'] = _LOG_FILE_DESTINATION
    if 'format' not in kwargs:
        kwargs['format'] = '{message}'
    if 'style' not in kwargs:
        kwargs['style'] = '{'
    if 'level' not in kwargs:
        kwargs['level'] = _GLOBAL_LOG_LEVEL

    logging.basicConfig(**kwargs)


def set_global_log_level(log_level: int, update_existing: bool = True):
    global _GLOBAL_LOG_LEVEL
    _GLOBAL_LOG_LEVEL = log_level

    if update_existing:
        for lgr in _registered_loggers:
            lgr.setLevel(log_level)


def register_logger(name: str, level: int = None) -> AdvancedLogger:
    """
    Creates, registers and returns a logger with a given name and level.
    Only if testing, it makes sure that no logger name is re-used

    Adds logger to _registered_loggers list, and wraps the log function to use our own
    As well as adds our own log_exception_info
    """
    assert name

    # Use the stdlib logging module to get our logger and set it's logging level
    # TODO swappable
    logging.setLoggerClass(AdvancedLogger)
    # noinspection PyTypeChecker
    _logger = logging.getLogger(_PREFIX + name)  # type: AdvancedLogger
    _logger.disabled = False
    _logger.setLevel(level=level or _GLOBAL_LOG_LEVEL)

    # Add it into our internal set of managed loggers if it isn't present
    if _logger not in _registered_loggers:
        _registered_loggers.add(_logger)

    # # TODO why was this line being done?
    # logging.setLoggerClass(_ORIGINAL_BASE_LOGGER_CLASS)

    return _logger


def deregister_logger(logger_or_name: Union[AdvancedLogger, str]):
    if isinstance(logger_or_name, str):
        lgr = _get_logger_by_name(logger_or_name)
    else:
        lgr = logger_or_name

    lgr.disabled = True
    _registered_loggers.remove(lgr)
    del logging.Logger.manager.loggerDict[lgr.name]
    del lgr


def _get_logger_by_name(name: str) -> AdvancedLogger:
    name = _PREFIX + name
    for lgr in _registered_loggers:
        if lgr.name == name:
            return lgr
    else:
        raise ValueError("Could not find logger matching name {}".format(name))


def clear_all_loggers(*, exact_filter: str = None, substr_filter: str = None, regex_filter: RE_TYPE = None):
    if substr_filter and regex_filter:
        raise ValueError("can't use both substr_filter and regex_filter")

    dereg_list = []

    for lgr in _registered_loggers:
        if exact_filter:
            if lgr.name == exact_filter:
                dereg_list.append(lgr)
        elif substr_filter:
            if substr_filter in lgr.name:
                dereg_list.append(lgr)
        elif regex_filter:
            if re.search(regex_filter, lgr.name):
                dereg_list.append(lgr)
        else:
            dereg_list.append(lgr)

    for lgr in dereg_list:
        deregister_logger(lgr)


def __should_log_random__(**kwargs):
    if 'out_of' in kwargs:
        likelihood = kwargs['likelihood'] if 'likelihood' in kwargs else 1
        if random_chance(likelihood, out_of=kwargs['out_of']):
            return True
        return False
    return True


def __log__(
        self, level=logging.INFO, msg=None,
        *args, exc_info=None, extra=None, stack_info=False,
        log_it=True, return_it=False, **kwargs
) -> Optional[str]:
    if not self.isEnabledFor(level):
        return
    if not __should_log_random__(**kwargs):
        return

    log_obj = {
        'meta': {
            'name': self.name,
            'time': datetime.utcnow(),
            'level': logging.getLevelName(level),
        },
        'msg': msg,
    }

    try:
        msg = json.dumps(cls=_AdvancedJSONEncoder, obj=log_obj)
    except Exception as e:
        self.log_exception_info(e, msg='Error while converting log msg to JSON')
        log_obj['msg'] = str(msg)
        msg = json.dumps(cls=_AdvancedJSONEncoder, obj=log_obj, )

    if log_it:
        # noinspection PyProtectedMember
        _CURRENT_BASE_LOGGER_CLASS._log(
            self=self,
            level=level,
            msg=msg,
            args=args, exc_info=exc_info, extra=extra, stack_info=stack_info
        )

    if return_it:
        return msg


def _log_exception_info(
        self,
        e: Union[Exception, str],
        *args,
        msg=None,
        log_it=True,
        return_it=False,
        **kwargs,
        # airline_code=None, route_code=None  # TODO
) -> Optional[Dict]:
    if not self.isEnabledFor(logging.CRITICAL):
        return
    if not __should_log_random__(**kwargs):
        return

    if isinstance(e, str) or e is None:
        formatted_tb = 'traceback not provided'
    else:
        tb = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)

        formatted_tb = []
        inner_formatted_tb = formatted_tb
        for line in tb:
            formatted_line, start_of_chained_exception = _format_traceback_line(line)
            inner_formatted_tb += formatted_line
            if start_of_chained_exception:
                inner_formatted_tb.append([])
                inner_formatted_tb = inner_formatted_tb[-1]

    obj = {
        'e': str(e),
        'traceback': formatted_tb,
        'msg': msg
    }

    if log_it:
        if 'indent' in kwargs:
            obj_as_str = json.dumps(obj, cls=_AdvancedJSONEncoder, indent=kwargs['indent'])
        else:
            obj_as_str = json.dumps(obj, cls=_AdvancedJSONEncoder)
        # noinspection PyProtectedMember
        _CURRENT_BASE_LOGGER_CLASS._log(
            self=self,
            level=logging.ERROR,
            msg=obj_as_str,
            args=args,
            exc_info=False,
        )

    if return_it:
        return obj


def _format_traceback_line(line: str) -> (List[_LOGGER_OUTPUT_TYPE], bool):
    """
    Takes in a traceback line by line
    :param line: the formatted line as a string
    :return: formatted line, whether this is a new line, or should be concat'd to the previously output line
    """
    out = []  # type: List[_LOGGER_OUTPUT_TYPE]
    raw_line = line

    # traceback's format uses hardcoded \n, so we split on that and not os.linesep
    line = line.replace(os.linesep, '\n')
    parsing_code_statement = False
    start_of_chained_exception = False

    for split_line in line.split('\n'):
        if not split_line:
            continue
        # remove extra path info, but not if it's something that just says the project name and isn't a path
        if split_line.strip().startswith('File '):
            try:
                if _PROJECT_DIR_NAME:
                    split_line = split_line[split_line.index(_PROJECT_DIR_NAME):]
            except ValueError:
                pass
            split_line = split_line.replace(os.path.sep, '.')

            match = re.match(r'^(.*)", (line [0-9]+), in (.+)$', split_line)
            if match:
                out.append([[match.group(1), match.group(2), match.group(3)]])
            else:
                out.append('no match for exception formatter, showing raw input')
                out.append(split_line)
                out.append(raw_line)
            parsing_code_statement = True
        elif parsing_code_statement:
            out[0].append(split_line)
        else:
            out.append(split_line)
            if split_line.endswith('another exception occurred:'):
                start_of_chained_exception = True

    return out, start_of_chained_exception


def random_chance(likelihood=1, out_of=1000) -> bool:
    return likelihood >= random.randint(1, out_of)
