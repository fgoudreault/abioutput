class DtsetParser:
    """Class that parses a dtset from an abinit output file.
    """
    def __init__(self, lines):
        # lines is a list of all the lines in the dtset
        self._lines = self._preprocess_lines(lines)
        self.data = self._get_data(self._lines)

    def _get_data(self, lines):
        # extract data from dtset
        return {}

    def _preprocess_lines(self, lines):
        # remove empty spaces around lines
        return [x.strip() for x in lines]

    @classmethod
    def from_string(cls, string):
        """Parses a dtset from a single string instead of a list of lines.
        """
        lines = string.split("\n")
        return cls(lines)
