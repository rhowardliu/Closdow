from time import (localtime, strftime, strptime)
from re import (fullmatch, VERBOSE, compile)
from datetime import datetime

time_pattern = compile(r'''
^
([01]\d|2[0123])    #Hours from 00 to 24
:
([012345]\d)$       #Minutes from 00 to 59
''',VERBOSE)


def check_if_format_acceptable(timestring):
    return time_pattern.fullmatch(timestring)

def convert_time_to_string(time):
    timestring = datetime.strftime(time, '%H:%M')
    return time

def convert_string_to_time(time_string):
    datetime_object = datetime.strptime(time_string, '%H:%M')
    return datetime_object.time()

def create_window_timestamp (name, state, time):
    ts = name + '.' + state + '.' + time
    return ts

def parse_window_timestamp (timestamp):
    name, state, time = timestamp.split('.',2)
    return name, state, time

