import logging
import abc


class BaseSubParser(abc.ABC):
    """SubParser Base class.
    """

    _loggerName = "SubParser"  # Name of the subparser logger
    subject = None
    trigger = None

    def __init__(self, loglevel=logging.INFO):
        logging.basicConfig()
        self._logger = logging.getLogger(self._loggerName)
        self._logger.setLevel(loglevel)
        self._ending_relative_index = None

    @property
    def ending_relative_index(self):
        if hasattr(self, "_ending_relative_index"):
            if self._ending_relative_index is not None:
                return self._ending_relative_index
        # if we are here, there is a dev error
        raise ValueError("Dev Error: ending_relative_index must be set (%s)." %
                         self.subject)

    @staticmethod
    def preprocess_lines(lines):
        return [x.strip("\n").strip() for x in lines]
