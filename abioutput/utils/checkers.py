from ..bases import BaseUtility
from .routines import search_in_all_subdirs
import os


class StatusChecker(BaseUtility):
    """Class that checks the status of a calculation directory.
    """
    _loggername = "StatusChecker"

    def __init__(self, directory, ignore=None, **kwargs):
        """Status checker init method.

        Parameters
        ----------
        directory : CalculationDir instance
                    The calculation directory.
        ignore : list, optional
                 Ignore these subdirectories when looking for files.
        """
        super().__init__(**kwargs)
        self.status = self._get_status(directory, ignore=ignore)

    def _get_status(self, directory, **kwargs):
        # check first if this is really a calculation direcectory
        self._logger.debug(f"Looking for {directory}'s status.")
        status = {"path": directory,
                  "name": os.path.basename(directory)}
        # look for log and output files
        log = search_in_all_subdirs(directory, fileending="log", **kwargs)
        out = search_in_all_subdirs(directory, infilename=".out", **kwargs)
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
        self.convergence_reached = False
        if self.calculation_finished:
            self.convergence_reached = self._get_convergence_from_file(filepath)

    def _get_convergence_from_file(self, filepath):
        self._logger.debug(f"Looking for convergence status in {filepath}.")


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
