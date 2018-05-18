from abipy.abio.outputs import AbinitOutputFile
from ..bases import BaseUtility
from .output_subparsers import DtsetParser
from .utils.abinit_vars import AbinitVarStrToNum
from collections import OrderedDict
import logging


class OutputParser(AbinitOutputFile, BaseUtility):
    """An ABINIT output file parser that gets data from an output file.

    Parameters
    ----------
    filepath : str
               The path to the output file.
    """
    _loggername = "OutputParser"

    def __init__(self, *args, **kwargs):
        BaseUtility.__init__(self, kwargs.pop("loglevel", logging.INFO))
        AbinitOutputFile.__init__(self, *args, **kwargs)

        self.data_per_dtset = self._get_data_per_dtset()
        self._output_vars_global = None
        self._output_vars_dataset = None

    def extract_output_variable(self, variable):
        # return an awway of all the values of the variable to get
        # in globals?
        glob_names = self.output_vars_global.keys()
        if variable in glob_names:
            return (self.output_vars_global[variable]["value"],
                    self.output_vars_global[variable]["units"])
        # specific to each dtset if multidtset?
        # first dtset name
        first = tuple(self.output_vars_dataset.keys())[0]
        dtset_names = self.output_vars_dataset[first].keys()
        if variable in dtset_names:
            # we want to return a vector of those values
            vector = []
            for jdtset, vars_dict in self.output_vars_dataset.items():
                vector.append(vars_dict[variable]["value"])
            return (vector, self.output_vars_dataset[first][variable]["units"])

    @property
    def output_vars_dataset(self):
        if self._output_vars_dataset is not None:
            return self._output_vars_dataset
        vars_dtsets = self.final_vars_dataset
        variables = OrderedDict()
        for jdtset, vars_dict in vars_dtsets.items():
            a = AbinitVarStrToNum(vars_dict)
            variables[jdtset] = a.data
        self._output_vars_dataset = variables
        return self.output_vars_dataset

    @property
    def output_vars_global(self):
        if self._output_vars_global is not None:
            return self._output_vars_global
        # we need to convert the variables given as a single string by abipy
        # in order that they are immediately usable
        a = AbinitVarStrToNum(self.final_vars_global)
        self._output_vars_global = a.data
        return self.output_vars_global

    def _get_data_per_dtset(self):
        data = []
        self._logger.debug("%i datasets found in output." % len(self.datasets))
        for jdtset, string_dtset in self.datasets.items():
            data.append(self._extract_data_from_dtset(string_dtset))
        return data

    def _extract_data_from_dtset(self, string):
        # string is a single string from a dtset.
        dtsetparser = DtsetParser.from_string(string,
                                              loglevel=self._logger.level)
        return dtsetparser.data
