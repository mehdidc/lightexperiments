import os
import types
import json
from utils import SingletonDecorator
from remote import client
import std

from CodernityDB.database import Database


@SingletonDecorator
class Light(object):
    config_default = os.path.join(os.getenv("HOME"),
                                  "work", "data", "config.light")
    db_default = os.path.join(os.getenv("HOME"), "work", "data", "exps.dat")

    modules = [std]

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
        # register all functions in all modules
        for m in self.modules:
            for func in m.register:
                self.register([func])

    def launch(self):
        self.db_filename = self.config.get("db", self.db_default)
        self.db_filename = self.db_filename.encode()  # why error ?
        read_only = self.config.get("read_only", False)
        self.db = Database(self.db_filename)
        if not self.db.exists():
            self.db.create()
            self.add_indexes()
        else:
            if read_only is True:
                self.db.open()
            else:
                self.db.open()

    def add_indexes(self):
        for m in self.modules:
            self.db = m.add_indexes(self.db)

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
        self.db.close()


if __name__ == "__main__":
    light = Light()
    light.launch()
    light.initials()
    light.file_snapshot()
    light.start_collect_stdout()
    light.end_collect_stdout()
    light.tag("light_test")
    light.tag("mmmm")
    light.endings()

    light.store_experiment()
    l=(light.db.get("tags", "mmmm", with_doc=True))

    for cur in light.db.get_many("start", start="2017-01-01 00:00:00", end="2016-01-01 00:00:00", with_doc=True):
        print(cur.get("doc").keys())
    light.close()
