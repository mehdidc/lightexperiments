import os
import types
import sys
import std
import hashlib
import cPickle as pickle
import glob


from pymongo import MongoClient

from utils import SingletonDecorator


import numpy as np


def clean(e):

    if type(e) == dict:
        for k, v in e.items():
            e[k] = clean(v)
        return e
    elif type(e) == list:
        return [clean(a) for a in e]
    elif type(e) == np.array or type(e) == np.ndarray:
        return e.tolist()
    elif type(e) == np.float32 or type(e) == np.float64:
        return float(e)
    elif type(e) == np.int32 or type(e) == np.int64:
        return int(e)
    else:
        return e


@SingletonDecorator
class Light(object):
    config_default = os.path.join(os.getenv("HOME"),
                                  "work", "data", "config.light")
    waiting_list_default = os.path.join(
        os.getenv("HOME"), "work", "data",
        "light_waiting_list")

    modules = [std]

    def __init__(self, config=None):
        if config is None:
            config = dict()
        self.config = config
        self.funcs = {}
        self.cur_experiment = self.new_experiment()
        self.register_all()
        self.db_loaded = False

    def register_all(self):
        # register all functions in all modules
        for m in self.modules:
            for func in m.register:
                self.register([func])

    def launch(self):
        try:
            self.client = MongoClient(self.config.get("host", "localhost"),
                                      self.config.get("port", 27017))
            self.db_main = self.client[self.config.get("db_name", "main")]
            self.db = self.db_main[self.config.get("collection_name",
                                   "main_collection")]
            self.db_blobs = self.db_main[
                self.config.get("collection_name_blobs", "blobs")]
            self.add_indexes()
            self.db_loaded = True
        except Exception:
            self.db_loaded = False

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
        if self.db_loaded is True:
            self.db.insert(e)
        else:
            m = hashlib.md5()
            m.update(str(self.cur_experiment))
            filename = m.hexdigest()
            filename = ("{0}/{1}.pkl".format(
                self.config.get("waiting_list", self.waiting_list_default),
                filename))
            fd = open(filename, "w")
            pickle.dump(self.cur_experiment, fd)
            fd.close()

        self.cur_experiment = None

    def new_experiment(self):
        return {}

    def close(self):
        if self.db_loaded:
            self.db_main.logout()
            self.client.close()

    def insert_blob(self, content):
        m = hashlib.md5()
        m.update(pickle.dumps(content))
        blob_hash = m.hexdigest()

        if self.db_loaded:
            self.db_blobs.insert(dict(content=content,
                                      blob_hash=blob_hash))
        else:
            filename = blob_hash

            filename = "{0}/{1}.blob".format(
                self.config.get("waiting_list", self.waiting_list_default),
                filename)
            fd = open(filename, "w")
            pickle.dump(content, fd)
            fd.close()
        return blob_hash

    def get_blob(self, _id=None, blob_hash=None):
        d = dict()
        if _id is not None:
            d["_id"] = _id
        if blob_hash is not None:
            d["blob_hash"] = blob_hash
        if self.db_loaded is True:
            return self.db_blobs.find_one(d).get("content")
        else:
            filename = (self.config.get("waiting_list",
                                        self.waiting_list_default) +
                        "/" + blob_hash + ".blob")
            fd = open(filename)
            content = pickle.load(fd)
            fd.close()
            return content

    def process_waiting_list(self):
        filenames = self.config.get("waiting_list",
                                    self.waiting_list_default)+"/*.pkl"
        for filename in glob.glob(filenames):
            print("Processing : {0}".format(filename))
            fd = open(filename)
            e = pickle.load(fd)
            fd.close()
            try:
                e = clean(e)
                self.store_experiment(e)
            except Exception as ex:
                errmsg = ("Could not deal with : {0}, exception : {1}".format(
                          filename, ex))
                print(errmsg)
                sys.exit(0)
            else:
                os.rename(filename, filename + ".bak")

        filenames = (self.config.get("waiting_list",
                     self.waiting_list_default)+"/*.blob")
        for filename in glob.glob(filenames):
            print("Processing : {0}".format(filename))
            fd = open(filename)
            content = pickle.load(fd)
            fd.close()
            try:
                content = clean(content)
                self.insert_blob(content)
                os.rename(filename, filename + ".bak")
            except Exception as ex:

                errmsg = ("Could not deal with : {0}, exception : {1}".format(
                          filename, ex))
                print(errmsg)
            else:
                os.rename(filename, filename + ".bak")
                sys.exit(0)

if __name__ == "__main__":
    light = Light()
    light.launch()
    light.initials()
    light.file_snapshot()
    light.start_collect_stdout()
    light.end_collect_stdout()
    light.tag("light_test")
    light.endings()
    id_ = light.insert_blob([111111, 1121])
    light.store_experiment()
    l = light.db.find({"tags": "light_test"})
    light.close()
