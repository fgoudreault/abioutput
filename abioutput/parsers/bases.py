import abc
import logging
import os


class BaseParser(abc.ABC):

    def __init__(self, loglevel=logging.WARNING):
        logging.basicConfig()
        self._logger = logging.getLogger(self._loggername)
        self._logger.setLevel(loglevel)

    @property
    @abc.abstractmethod
    def _loggername(self):
        pass


class BaseParserPathChecker(BaseParser):
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
