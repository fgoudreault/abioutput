from .eig_parser import EIGParser
from .base import BaseSubParser
import logging


SUBPARSERS = (EIGParser, )


class SubParsersList:
    def __init__(self, slist):
        self.subparsers = {trigger: subparser for trigger, subparser in
                           zip([s.trigger for s in slist], slist)}

    def items(self):
        return self.subparsers.items()

    def remove(self, parser):
        del self.subparsers[parser.trigger]


class DtsetParser(BaseSubParser):
    """Class that parses a dtset from an abinit output file.
    """
    _loggerName = "DtsetParser"
    subject = "dtset"
    trigger = "== DATASET"

    def __init__(self, lines, loglevel=logging.INFO):
        super().__init__(loglevel=loglevel)
        self._logger.debug("=== Parsing DATASET ===")
        # lines is a list of all the lines in the dtset
        # The lines given here are only the lines of one dataset
        # Thanks to abipy this is possible!
        self._lines = self.preprocess_lines(lines)
        # this is a bit irrelevent here but still though...
        self._ending_relative_index = len(self._lines)
        # extract data with the help of subparsers
        self.data = self._get_data(self._lines)

    def _get_data(self, lines):
        data = {}
        # extract data from dtset
        skip = 0
        subparsers = SubParsersList(SUBPARSERS)
        for index, line in enumerate(lines):
            if index < skip:
                # don't work on this line
                continue
            for trigger, subparser in subparsers.items():
                if trigger in line:
                    # this line is a trigger for the subparser to work
                    # parse the rest of the lines from here
                    s = subparser(lines[index:], loglevel=self._logger.level)
                    data[s.subject] = s.data
                    # remove the subparser from the list to not parse again
                    subparsers.remove(subparser)
                    # modify the skip to not reparse the parsed lines
                    skip = index + s.ending_relative_index
                    # stop parsing the active line
                    break
        return data

    @classmethod
    def from_string(cls, string, **kwargs):
        """Parses a dtset from a single string instead of a list of lines.
        """
        lines = string.split("\n")
        return cls(lines, **kwargs)
