import os
import types

import json
from unqlite import UnQLite

from utils import SingletonDecorator
from remote import client
import std


@SingletonDecorator
class Light(object):
    config_default = os.path.join(os.getenv("HOME"),
                                  "work", "data", "config.light")
    db_default = os.path.join(os.getenv("HOME"), "work", "data", "exps.dat")

    def __new__(cls, config=None):
        if config is None:
            try:
                config = json.load(open(cls.config_default))
            except Exception:
                config = {}
        if (config.get("uri") is not None and config.get("remote", False) is False):
            return client.proxy(config.get("uri"))
        else:
            obj = object.__new__(cls)
            obj.config = config
            return obj

    def __init__(self, config=None):
        self.funcs = {}
        self.cur_experiment = self.new_experiment()
        self.register_all()

    def register_all(self):
        modules = [std]
        # register all functions in all modules
        for m in modules:
            for func in m.register:
                self.register([func])

    def launch(self):
        self.db_filename = self.config.get("db", self.db_default)
        self.db_filename = self.db_filename.encode()  # why error ?
        self.db = UnQLite(database=self.db_filename)
        self.experiments = self.db.collection('experiments')
        self.experiments.create()

    def register(self, funcs):
        for func in funcs:
            def f(s, *args, **kwargs):
                return func(self.cur_experiment, *args, **kwargs)
            try:
                f.__name__ = func.__name__
                setattr(self.__class__,
                        func.__name__,
                        types.MethodType(f, None, self.__class__))
                setattr(self, func.__name__,
                        types.MethodType(f, self, self.__class__))
            except Exception, e:
                print(e)

    def __getattr__(self, v):
        if v in self.funcs:
            return self.funcs.get(v)
        else:
            raise AttributeError(v)

    def store_experiment(self, e=None):
        if e is None:
            e = self.cur_experiment
        self.experiments.store([e])
        self.db.commit()
        self.cur_experiment = None

    def new_experiment(self):
        return {}

    def close(self):
        self.db.close()


if __name__ == "__main__":
    light = Light()
    light.launch()
    light.file_snapshot()
    light.start_collect_stdout()
    light.end_collect_stdout()
    light.tag("light_test")
    light.date()
    light.store_experiment()
