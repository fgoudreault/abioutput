from .bases import BaseBuilder
from .status_checkers import StatusChecker
import os


class CalculationDir(BaseBuilder):
    """Class that represents a calculation directory.
    """
    _loggername = "CalculationDir"

    def __init__(self, directory, **kwargs):
        """CalculationDir init method.

        Parameters
        ----------
        directory : str
                    The calculation directory.
        """
        super().__init__(directory, **kwargs)
        if not self.is_calculation_dir(directory):
            raise FileNotFoundError(f"No input file found in {directory}.")

    def _set_main_directory(self, directory_name):
        self.path = directory_name

    @property
    def status(self):
        checker = StatusChecker(self.path)
        return checker.status

    @staticmethod
    def is_calculation_dir(directory):
        # check if this directory is a calculation directory
        # to see if it is one, check if an input file (.in) is present
        # in the directory. If yes, than it is considered a calculation dir
        if not os.path.isdir(directory):
            raise NotADirectoryError(f"{directory} is not a directory.")
        entries = os.listdir(directory)
        files = [x for x in entries if
                 os.path.isfile(os.path.join(directory, x))]
        for f in files:
            if f.endswith(".in"):
                # found an input file
                return True
        return False
