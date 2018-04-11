import logging
import os


class DMFTBaseParser:
    _loggername = None

    def __init__(self, path, loglevel=logging.WARNING):
        if self._loggername is None:
            raise ValueError("Dev error: parser don't have a logger name.")
        logging.basicConfig()
        self._logger = logging.getLogger(self._loggername)
        self._logger.setLevel(loglevel)

        # check that path exists
        if not os.path.exists(path) or not os.path.isfile(path):
            raise OSError("%s is not a valid file path..." % path)

    def __getitem__(self, indices):
        return self.data[indices]
