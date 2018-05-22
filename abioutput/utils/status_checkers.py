from ..bases import BaseUtility
from tabulate import tabulate
from colorama import Fore, Style
import abc
import colorama
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


class TreeBuilder(BaseBuilder):
    """Object that starts at the top of a directory tree and scrolls down
    in all its subdirectories in order to get the status of each abinit
    calculations. The status is checked by looking at the log file for the
    'Calculation completed.' keyword.

    When looking down in the tree, we assume that a caculation directory
    does not have subdirectories containing other calculations
    (this may be a future feature to look down everywhere).
    """
    _loggername = "TreeBuilder"

    def __init__(self, top_directory, **kwargs):
        """TreeBuilder init method.

        Parameters
        ----------
        top_directory : str
                        The top directory path.
        """
        super().__init__(top_directory, **kwargs)
        self._logger.info(f"Computing calculation tree status from"
                          f" {self._top_directory}")
        self.tree = self._get_tree(self._top_directory)

    def _set_main_directory(self, directory_name):
        self._top_directory = directory_name

    def _get_tree(self, top_directory):
        # check if current dir is a calculation directory
        if CalculationDir.is_calculation_dir(top_directory):
            self._logger.debug(f"Found a calculation directory:"
                               f" {top_directory}")
            return [CalculationDir(top_directory)]
        # if not, look in all subdirectories
        subentries = os.listdir(top_directory)
        subdirs = [os.path.join(top_directory, x)
                   for x in subentries if os.path.isdir(x)]
        status = []
        for subdir in subdirs:
            status += self._get_tree(os.path.join(top_directory,
                                                  subdir))
        return status

    @property
    def status(self):
        status = []
        self._logger.info("Computing status of calculation tree.")
        for calc in self.tree:
            status.append(calc.status)
        return status

    def print_status(self, shortpath=True):
        """Prints the status of each calculation in the calculation tree.

        Parameters
        ----------
        shortpath : bool, optional
                    If False, the full path to the calculation directories are
                    given instead of relative paths.
                    If True, the relative path to the current directory (where
                    the script is executed) is given instead.
        """
        colorama.init(autoreset=True)
        calcs = []
        status = []
        for calculation in self.status:
            path = calculation["path"]
            if shortpath:
                path = os.path.relpath(path)
            calcs.append(path)
            started = calculation["calculation_started"]
            finished = calculation["calculation_finished"]
            if not started:
                status.append(self._get_print_text("NOT STARTED",
                                                   color=Fore.RED,
                                                   style=Style.BRIGHT))
                continue
            elif started and not finished:
                status.append(self._get_print_text("RUNNING",
                                                   color=Fore.YELLOW,
                                                   style=Style.BRIGHT))
                continue
            elif started and finished:
                status.append(self._get_print_text("COMPLETED",
                                                   color=Fore.GREEN,
                                                   style=Style.BRIGHT))
                continue
        print(tabulate([[c, s] for c, s in zip(calcs, status)],
                       headers=["Calculation", "Status"]))

    def _get_print_text(self, text, color="", style=""):
        # returns colored and styled string
        return style + color + text + colorama.Style.RESET_ALL


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
        checker = StatusChecker(self)
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


class StatusChecker(BaseUtility):
    """Class that checks the status of a calculation directory.
    """
    _loggername = "StatusChecker"

    def __init__(self, directory, **kwargs):
        """Status checker init method.

        Parameters
        ----------
        directory : CalculationDir instance
                    The calculation directory.
        """
        super().__init__(**kwargs)
        if not isinstance(directory, CalculationDir):
            raise ValueError("directory must be a CalculationDir instance.")
        self.status = self._get_status(directory.path)

    def _get_status(self, directory):
        # check first if this is really a calculation direcectory
        self._logger.debug(f"Looking for {directory}'s status.")
        status = {"path": directory,
                  "name": os.path.basename(directory)}
        # look for log and output files
        log = self._look_in_all_subdirs(directory, fileending="log")
        out = self._look_in_all_subdirs(directory, infilename=".out")
        if len(log) == 0 and len(out) == 0:
            # no log and output file found.
            # this means that computation has not started or that files were
            # named in a non convenient way.
            # We assume here that files were correctly named
            status["calculation_started"] = False
            status["calculation_finished"] = False
            self._logger.debug("Calculation has not started.")
            return status

        elif len(log) == 0:
            # no log found but an output was found, check status from output
            if len(out) > 1:
                raise LookupError(f"More than one output was found in,"
                                  f" {directory} and no log found...")
            self._logger.debug("Looking in output file for status.")
            finished = self._dig_file_for_status(out[0])
            # if output file exists, calculation has started
            status["calculation_started"] = True
            status["calculation_finished"] = finished
            return status

        elif len(log) > 1:
            # wtf more than one log file??
            raise LookupError(f"More than 1 log file found in {directory}.")
        # get status from log file (prefered behavior)
        self._logger.debug("Looking in log file for status.")
        finished = self._dig_file_for_status(log[0])
        status["calculation_started"] = True
        status["calculation_finished"] = finished
        return status

    def _dig_file_for_status(self, filepath):
        # check in the file to get the computation status
        checker = FileStatusChecker(filepath, loglevel=self._logger.level)
        return checker.calculation_finished

    def _look_in_all_subdirs(self, top_directory, filename=None,
                             infilename=None,
                             filestarting="", fileending="",
                             expected=None):
        # find all files in the directory and in its subdirectories that
        # matches the pattern.
        # start by listing the path of all files
        files = self._get_all_subfiles(top_directory)
        to_return = []
        for f in files:
            name = os.path.basename(f)
            if filename is not None:
                if name == filename:
                    to_return.append(f)
                # don't consider other criterion
                continue
            if infilename is not None:
                if infilename in name:
                    to_return.append(f)
                # don't consider other criterion
                continue
            if name.startswith(filestarting) and name.endswith(fileending):
                to_return.append(f)
        if expected is not None:
            # check if number of files found matches what was expected
            if expected != len(to_return):
                raise ValueError("Found more or less files as expected.")
        return to_return

    def _get_all_subfiles(self, top_directory):
        # return a list of the path of all files and subfiles in this dir.
        entries = os.listdir(top_directory)
        files_here = [os.path.join(top_directory, x)
                      for x in entries
                      if os.path.isfile(os.path.join(top_directory, x))]
        files = files_here
        for subdir in [os.path.join(top_directory, x)
                       for x in entries
                       if os.path.isdir(os.path.join(top_directory, x))]:
            files += self._get_all_subfiles(subdir)
        return files


class FileStatusChecker(BaseUtility):
    """Class that checks the status of a computation from the log or out file.
    """
    _loggername = "FileStatusChecker"

    def __init__(self, filepath, **kwargs):
        """File status checker init method.

        Parameters
        ----------
        filepath = str
                   The path of the log/out file to look into.
        """
        super().__init__(**kwargs)
        if not os.path.isfile(filepath) or not os.path.exists(filepath):
            raise FileNotFoundError(f"{filepath} not a valid file path.")
        self.calculation_finished = self._get_status_from_file(filepath)

    def _get_status_from_file(self, filepath):
        self._logger.debug(f"Looking for calculation status in {filepath}.")
        with open(filepath) as f:
            lines = f.readlines()
        # loop over the last 200 lines to find if calculation done
        for i, line in enumerate(lines[::-1]):
            if i == 200:
                # if after 200 lines keywords are not found, this means that
                # calculation is not finished. This is a mean to stop looking
                # in case file is zillions of lines long.
                self._logger.debug("Calculation has not finished.")
                return False
            if "Calculation completed." in line:
                self._logger.debug("Calculation is finished.")
                return True
