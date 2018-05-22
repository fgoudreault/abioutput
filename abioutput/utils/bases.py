from ..bases import BaseUtility
import abc
import os


class BaseBuilder(BaseUtility):
    """Base class for all status checkers.
    """
    def __init__(self, directory, **kwargs):
        super().__init__(**kwargs)
        directory = os.path.abspath(os.path.expanduser(directory))
        if not os.path.exists(directory) or not os.path.isdir(directory):
            raise NotADirectoryError(f"{directory} is not a valid path.")
        self._set_main_directory(directory)

    @abc.abstractmethod
    def _set_main_directory(self, *args):
        pass
