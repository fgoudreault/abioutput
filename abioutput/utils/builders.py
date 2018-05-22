from .bases import BaseBuilder
from .calculation_dir import CalculationDir
from tabulate import tabulate
from colorama import Fore, Style
import colorama
import os


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
