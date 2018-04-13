from .bases import DataFileParser
from .utils._common_routines import decompose_line
import numpy as np


class FatbandParser(DataFileParser):
    _loggername = "FatbandParser"

    def __init__(self, *args, **kwargs):
        """Parser that reads a FATBAND file.

        Parameters
        ----------
        path : str
               The path to the FATBAND ABINIT file.
        loglevel : int, optional
                   The logging level.
        """
        super().__init__(*args, **kwargs)
        self.data = self._extract_data(self.filepath)
        self.nkpt = self.data.shape[1]
        self.nband = self.data.shape[0]
        self._logger.info("Data extracted.")
        self._logger.debug("Fatbands calculation: %i bands and %i kpts" %
                           (self.nband, self.nkpt))

    def _extract_data(self, path):
        self._logger.info("Starting to extract data.")
        with open(path) as f:
            lines = f.readlines()

        data = []
        end = 0
        for i, line in enumerate(lines):
            if i < end:
                continue
            if line.startswith("# BAND"):
                band, skip = self._extract_data_band_block(lines[i:])
                data.append(band)
                end += skip
        # data should be nband x nkpt x 2
        # where the last axis is the eigenvalue followed by the character
        return np.array(data)

    def _extract_data_band_block(self, lines):
        self._logger.debug("Extracting data from one band block.")
        block_end = False
        data = []
        for i, line in enumerate(lines):
            if line.startswith("# BAND") or (line.startswith("&") or not
                                             len(line.rstrip("\n"))):
                if not block_end:
                    block_end = True
                    continue
                else:
                    return data, i
            s, i, f = decompose_line(line)
            if len(f) != 2 or len(i) != 1:  # should be 2 numbers + kpt index
                self._logger.error("Error while extracting data from: '%s'" %
                                   line)
                raise LookupError("Error while reading fatband file.")
            data.append(f)
        return data, len(lines) - 1
