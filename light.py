import os

import json
from unqlite import UnQLite

modules = ["std", "ext.sci"]


class Light(object):
    config_file = "config.light"
    db_default = os.path.join(os.getenv("HOME"), "work", "data", "exps.dat")
    config = None

    def __init__(self):
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

light = Light()


def init():
    try:
        light.config = json.load(open(light.config_file, "r"))
    except Exception:
        light.config = {}

    light.db_filename = light.config.get("db", light.db_default)
    light.db_filename = light.db_filename.encode()  # why error ?
    light.db = UnQLite(database=light.db_filename)
    light.experiments = light.db.collection('experiments')
    light.cur_experiment = new_experiment()


def store_experiment(e=None):
    if e is None:
        e = light.cur_experiment
    light.experiments.store([e])
    light.db.commit()
    light.cur_experiment = None


def new_experiment():
    return {}

if __name__ == "__main__":
    init()

    light.file_snapshot()
    light.start_collect_stdout()
    print("m")
    light.end_collect_stdout()
    light.tag("tag1")
    light.tag("tag2")

    store_experiment()
