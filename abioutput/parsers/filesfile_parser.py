from .bases import DataFileParser


class FilesFileParser(DataFileParser):
    """Parser that parses a files file.
    """
    _loggername = "FileFileParser"

    def __init__(self, path, **kwargs):
        """FilesFile parser init method.

        Parameters
        ----------
        path : str
               The path to the files file.
        """
        super().__init__(path, **kwargs)
        if not path.endswith(".files"):
            self._logger.warning(f"File path {path} might not be"
                                 f" a files file.")
        self.data = self._get_data(path)

    def _get_data(self, path):
        data = {}
        with open(path) as f:
            lines = f.readlines()
        lines = [l.strip().strip("\n") for l in lines]
        lines = [l for l in lines if not (l.startswith("#") or len(l) == 0)]
        data["input_path"] = lines[0]
        data["output_path"] = lines[1]
        data["input_prefix"] = lines[2]
        data["output_prefix"] = lines[3]
        data["tmp_prefix"] = lines[4]
        data["pseudos"] = [x for x in lines[5:]]
        return data
