from .bases import BaseBuilder
from .routines import search_in_all_subdirs
from .status_checkers import StatusChecker
from abioutput.parsers import FilesFileParser, OutputParser
import os



class CalculationDir(BaseBuilder):
    """Class that represents a calculation directory.
    """
    _loggername = "CalculationDir"

    def __init__(self, directory, ignore=None, **kwargs):
        """CalculationDir init method.

        Parameters
        ----------
        directory : str
                    The calculation directory.
        ignore : list, optional
                 If not None, this list of directories will be ignored while
                 searching for the corresponding calculation files.
        """
        super().__init__(directory, **kwargs)
        if not self.is_calculation_dir(directory):
            raise FileNotFoundError(f"No input file found in {directory}.")
        self._ignore = ignore
        self.filesfile = FilesFileParser(self._get_files_file(ignore=ignore),
                                         loglevel=self._logger.level)
        self.inputfile = self._get_input_file(ignore=ignore)
        self._outputfile = None

    @property
    def outputfile(self):
        if self._outputfile is not None:
            return self._outputfile
        if not self.status["calculation_finished"]:
            raise LookupError("Calculation is not finished,"
                              " cannot analyse output file.")
        self._outputfile = OutputParser(self.filesfile["output_path"])
        return self._outputfile
    
    @property
    def is_calculation_converged(self):
        # check if computation is finished
        try:
            out = self.outputfile
        except LookupError:
            self._logger.error("Cannot read convergence if computation is not finished.")
            return False
        iscf = self.get_output_var("iscf")[0]
        if iscf < 0:
            # NON SCF CALCULATION => cannot tell if convergence is reached
            raise ValueError(f"iscf={iscf}<0 => cannot tell if conv. is reach")
        ionmov = self.get_output_var("ionmov")
        if ionmov is not None:
            ionmov = ionmov[0]
        else:
            ionmov = 0
        if ionmov > 0:
            # ionmov calculation => check for Force convergence
            return self._dig_output_for_convergence("gradients are converged",
                                                    "not enough Broyd/MD steps to converge gradients")
        # standard GS calculation
        return self._dig_output_for_convergence("converged",
                                                "not enough SCF cycles to converge")

    def _dig_output_for_convergence(self, converged_keywords, nonconverged_keywords):
        with open(self.filesfile["output_path"]) as f:
            lines = f.readlines()
        for line in lines[::-1]:
            if converged_keywords in line:
                return True
            elif nonconverged_keywords in line:
                return False
        # if we are here, computation is not finished => return False
        self._logger.warning("Could not find the convergence status...")
        return False        

    def get_output_var(self, outputvar):
        """Returns the value of an output variable from this calculation.

        Parameters
        ----------
        outputvar : str
                    The name of the output variable.
        """
        self._logger.debug(f"Extracting {outputvar} from output file.")
        return self.outputfile.extract_output_variable(outputvar)

    def _get_files_file(self, **kwargs):
        return search_in_all_subdirs(self.path, fileending=".files",
                                     expected=1, **kwargs)[0]
    
    def _get_input_file(self, **kwargs):
        return search_in_all_subdirs(self.path, fileending=".in",
                                     expected=1, **kwargs)[0]

    def _set_main_directory(self, directory_name):
        self.path = directory_name

    @property
    def status(self):
        checker = StatusChecker(self.path, self._ignore)
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
