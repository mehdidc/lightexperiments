import sys
import os

from io import TextIOWrapper, BytesIO
from light import light


def append(e, name, value):
    if name not in e:
        e[name] = []
    e[name].append(value)
    return e


def tag(e, tag):
    return append(e, "tags", tag)


def file_snapshot(e, label=None, filename=None):
    if e is None:
        e = light.cur_experiment
    if label is None:
        label = ""
    if filename is None:
        filename = os.path.join(os.getcwd(), sys.argv[0])
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
