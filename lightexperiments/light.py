import os
import types
import json
from utils import SingletonDecorator
import std
from pymongo import MongoClient


@SingletonDecorator
class Light(object):
    config_default = os.path.join(os.getenv("HOME"),
                                  "work", "data", "config.light")
    db_default = os.path.join(os.getenv("HOME"), "work", "data", "exps.dat")

    modules = [std]

    def __init__(self, config=None):
        if config is None:
            config = dict()
        self.config = config
        self.funcs = {}
        self.cur_experiment = self.new_experiment()
        self.register_all()

    def register_all(self):
        # register all functions in all modules
        for m in self.modules:
            for func in m.register:
                self.register([func])

    def launch(self):
        self.db_filename = self.config.get("db", self.db_default)
        self.db_filename = self.db_filename.encode()
        self.client = MongoClient(self.config.get("host", "localhost"),
                                  self.config.get("port", 27017))
        self.db_main = self.client[self.config.get("db_name", "main")]
        self.db = self.db_main[self.config.get("collection_name",
                                               "main_collection")]
        self.add_indexes()

    def add_indexes(self):
        for m in self.modules:
            self.dbn = m.add_indexes(self.db)

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
        self.db.insert(e)
        self.cur_experiment = None

    def new_experiment(self):
        return {}

    def close(self):
        self.db_main.logout()
        self.client.close()

if __name__ == "__main__":
    light = Light()
    light.launch()
    light.initials()
    light.file_snapshot()
    light.start_collect_stdout()
    light.end_collect_stdout()
    light.tag("light_test")
    light.endings()

    light.store_experiment()
    l = light.db.find({"tags": "light_test"})
    print(list(l))
    light.close()
