import os

import json
from unqlite import UnQLite

modules = ["std", "ext.sci"]


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
        self.cur_experiment = new_experiment()
        self.cache = {}

    def __getattr__(self, v):
        if v in self.cache:
            return self.cache[v]
        for m in modules:
            module = __import__(m)
            if v in module.__dict__:
                m = getattr(module, v)

                def f(*args, **kwargs):
                    return m(light.cur_experiment, *args, **kwargs)
                self.cache[v] = f
                return f
        return None


def store_experiment(e=None):
    if e is None:
        e = light.cur_experiment
    light.experiments.store([e])
    light.db.commit()
    light.cur_experiment = None


def new_experiment():
    return {}


light = Light()

if __name__ == "__main__":

    light.file_snapshot()
    light.start_collect_stdout()
    print("m")
    light.end_collect_stdout()
    light.tag("tag1")
    light.tag("tag2")

    store_experiment()
