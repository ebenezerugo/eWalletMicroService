import logging
from functools import wraps
from datetime import datetime, time
from django.db import connection
from pprint import pprint

logging.basicConfig(level=logging.DEBUG)


def delta_to_datetime(_d):
    return datetime.combine(datetime.today().date(), time(0, 0)) + _d


class Timer(object):

    def __init__(self, identifier=''):
        self.identifier = identifier

    def __enter__(self):
        self.start = datetime.now()
        return self

    def __exit__(self, *args):
        self.end = datetime.now()
        self.interval = self.end - self.start
        _time = delta_to_datetime(self.interval)
        self.time = _time
        logging.info('%s | runtime: %s m, %s s, %s ms', self.identifier, _time.minute, _time.second,
                     _time.microsecond // 1000)


def track_runtime(func):
    @wraps(func)
    def timed(*args, **kwargs):
        with Timer(func.__name__):
            result = func(*args, **kwargs)
        return result

    return timed


class DBProfiler(object):

    def __init__(self, identifier=''):
        self.identifier = identifier

    def __enter__(self):
        self.initial = len(connection.queries)
        return self

    def __exit__(self, *args):
        self.final = len(connection.queries)
        self.count = self.final - self.initial
        for query in connection.queries:
            print(query)
        logging.info('%s | database: %s queries', self.identifier, self.count)


def track_database(func):
    @wraps(func)
    def tracked(*args, **kwargs):
        with DBProfiler(func.__name__):
            result = func(*args, **kwargs)
        return result

    return tracked
