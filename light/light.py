import os

import json
from unqlite import UnQLite

from importlib import import_module



class Light(object):
    config_file = "config.light"
    db_default = os.path.join(os.getenv("HOME"), "work", "data", "exps.dat")
    config = None

    def __init__(self):
        try:
            self.config = json.load(open(light.config_file, "r"))
        except Exception:
            self.config = {}

        self.db_filename = self.config.get("db", self.db_default)
        self.db_filename = self.db_filename.encode()  # why error ?
        self.db = UnQLite(database=self.db_filename)
        self.experiments = self.db.collection('experiments')
        self.cur_experiment = self.new_experiment()
        self.funcs = {}

    def register(self, funcs):
        for func in funcs:
            def f(*args, **kwargs):
                return func(self.cur_experiment, *args, **kwargs)
            self.funcs[func.__name__] = f

    def __getattr__(self, v):
        return self.funcs.get(v)

    def store_experiment(self, e=None):
        if e is None:
            e = self.cur_experiment
        self.experiments.store([e])
        self.db.commit()
        self.cur_experiment = None

    def new_experiment(self, ):
        return {}


light = Light()

import std

modules = [std]

for m in modules:
    for func in m.__dict__.keys():
        if not func.startswith("__"):
            light.register([m.__dict__[func]])


if __name__ == "__main__":
    light.file_snapshot()
    light.start_collect_stdout()
    light.end_collect_stdout()
    light.tag("tag1")
    light.tag("tag2")

    light.store_experiment()
