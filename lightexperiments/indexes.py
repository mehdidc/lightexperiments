from CodernityDB.hash_index import MultiHashIndex
from CodernityDB.tree_index import TreeBasedIndex


class TagIndex(MultiHashIndex):

    custom_header = """from CodernityDB.hash_index import MultiHashIndex"""

    def __init__(self, *args, **kwargs):
        self.length = kwargs.get("length", 100)
        kwargs['key_format'] = '{0}s'.format(self.length)
        super(TagIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        tag_val = data.get(self.name)
        if tag_val is not None:
            out = set()
            for val in tag_val:
                out.add(val.rjust(self.length, "_").lower())
            return out, None
        return None

    def make_key(self, key):
        return key.rjust(self.length, "_").lower()


class DatetimeIndex(TreeBasedIndex):

    custom_header = """from CodernityDB.tree_index import TreeBasedIndex"""

    def __init__(self, *args, **kwargs):
        kwargs["node_capacity"] = 10
        kwargs["key_format"] = "{0}s".format(kwargs.get("length", 26))
        super(DatetimeIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        v = data.get(self.name)
        if v is not None:
            return v, None
        return None

    def make_key(self, key):
        return key

class FloatIndex(TreeBasedIndex):

    custom_header = """from CodernityDB.tree_index import TreeBasedIndex"""

    def __init__(self, *args, **kwargs):
        kwargs["node_capacity"] = 10
        kwargs["key_format"] = "f"
        super(FloatIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        v = data.get(self.name)
        if v is not None:
            return v, None
        return None

    def make_key(self, key):
        return key
