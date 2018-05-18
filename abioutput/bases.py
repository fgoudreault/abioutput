import abc
import logging


class BaseUtility(abc.ABC):

    def __init__(self, loglevel=logging.WARNING):
        logging.basicConfig()
        self._logger = logging.getLogger(self._loggername)
        self._logger.setLevel(loglevel)

    @property
    @abc.abstractmethod
    def _loggername(self):
        pass
