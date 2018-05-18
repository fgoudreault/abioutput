from ..bases import BaseUtility
import os


class BaseParserPathChecker(BaseUtility):
    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self._check_file_exists(path)
        self.filepath = path

    def _check_file_exists(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Nothing found here: {path}.")
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Not a file: {path}.")


class DataFileParser(BaseParserPathChecker):
    def __getitem__(self, key):
        return self.data[key]
