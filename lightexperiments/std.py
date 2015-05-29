import sys
import os

from io import TextIOWrapper, BytesIO

import datetime as dt


def initials(e):
    e = date(e)
    e = duration_start(e)
    return e


def endings(e):
    e = duration_end(e)
    return e


datetime_format = "%Y-%m-%d %H:%M:%S"
def date(e):
    e["datetime"] = dt.datetime.now().strftime(datetime_format)
    return e


def duration_start(e):
    e["start"] = dt.datetime.now()
    return e


def duration_end(e):
    e["end"] = dt.datetime.now()
    e["duration"] = (e["end"] - e["start"]).total_seconds()
    e["start"] = e["start"].strftime(datetime_format)
    e["end"] = e["end"].strftime(datetime_format)
    return e

def append(e, name, value):
    if name not in e:
        e[name] = []
    e[name].append(value)
    return e


def tag(e, tag):
    return append(e, "tags", tag)


def file_snapshot(e, label=None, filename=None):
    if e is None:

        from light import Light
        e = Light().cur_experiment
    if label is None:
        label = ""
    if filename is None:
        filename = os.path.join(os.getcwd(), sys.argv[0])
        if os.path.isdir(filename):
            return e
    e["code_%s" % (label,)] = open(filename, "r").read()
    return e


class StdoutBuffer(TextIOWrapper):
    def write(self, string):
        try:
            return super(StdoutBuffer, self).write(string)
        except TypeError:
            # redirect encoded byte strings directly to buffer
            return super(StdoutBuffer, self).buffer.write(string)


def start_collect_stdout(e):
    e["old_stdout"] = sys.stdout
    sys.stdout = StdoutBuffer(BytesIO(), sys.stdout.encoding)
    return e


def end_collect_stdout(e):
    sys.stdout.seek(0)
    e["stdout"] = sys.stdout.read()
    sys.stdout = e["old_stdout"]
    del e["old_stdout"]
    return e


def set_seed(e, seed):
    e["seed"] = seed
    return e

def set(e, k, v):
    e[k] = v
    return e


from indexes import TagIndex, DatetimeIndex, FloatIndex


def add_indexes(db):
    db.add_index(TagIndex(db.path, "tags"))
    db.add_index(DatetimeIndex(db.path, "start"))
    db.add_index(DatetimeIndex(db.path, "end"))
    db.add_index(FloatIndex(db.path, "duration"))
    return db

register = [
    initials,
    endings,
    date,
    duration_start,
    duration_end,
    append,
    tag,
    file_snapshot,
    start_collect_stdout,
    end_collect_stdout,
    set_seed,
    set
]
