import numpy as np
from ..bases import DataFileParser
from ..utils._common_routines import decompose_line


class DMFTEigParser(DataFileParser):
    """Class that reads a .eig file produced by the DMFT module of Abinit.
    """
    _loggername = "DMFT_eig_parser"
    
    def __init__(self, *args, **kwargs):
        """The .eig file parser init method.

        Parameters
        ----------
        path : str
               The path to the .eig file.
        loglevel : int, optional
                   The logging level.
        """
        super().__init__(*args, **kwargs)
        self.data = self._read_data_from_file(self.filepath)

    def _read_data_from_file(self, path):
        self._logger.info("Extracting eigenvalues from %s" % path)
        with open(path, 'r') as f:
            lines = f.readlines()
        # DATA ORGANIZED AS FOLLOWS:
        # META DATA HEADER ...
        # For spin
        #           1
        # For k-point
        #           1
        # 1         1    value
        # 2         1    value
        # ...
        # nband     1    value
        # For k-point
        #           2
        # 1         2    value
        # ...

        # First strip header
        body, header = self._strip_header(lines)
        # extract meta data from header
        self._extract_meta_data(header)
        # extract data for each spin, kpt and considered band
        return np.array(self._extract_data(body))

    def _extract_data(self, body):
        self._logger.debug("Starting data extraction.")
        # extract eigenvalues data
        data = []
        end = 0
        for i, line in enumerate(body):
            if i < end:
                # skip lines until end of spin clock
                continue
            if "For spin" in line:
                data_per_spin, rel_end = self._extract_data_per_spin(body[i:])
                # check that number of kpts matches header
                if len(data_per_spin) != self.nkpt:
                    raise ValueError("Was expecting %i kpts but found %i" %
                                     (self.nkpt, len(data_per_spin)))
                assert len(data_per_spin) == self.nkpt
                data.append(data_per_spin)
                end += rel_end
        # check that number of spins matches header
        assert len(data) == self.nspins
        if len(data) == 1:
            # only one spin; return first block directly
            return data[0]
        return data

    def _extract_data_per_spin(self, lines):
        self._logger.debug("Starting data extraction for one spin.")
        # extract eigenvalues for a spin block
        data = []
        end = 0
        block_end = False
        for i, line in enumerate(lines):
            if i < end:
                continue
            if "For spin" in line:
                if not block_end:
                    continue
                # arrived at end of file or spin block
                return data, i
            if "For k-point" in line:
                data_per_kpt, rel_end = self._extract_data_per_kpt(lines[i:])
                # check that number of eigenvalues matches number of bands
                if len(data_per_kpt) != self.nband:
                    raise ValueError("Was expecting %i bands but found %i" %
                                     (self.nband, len(data_per_kpt)))
                block_end = True
                data.append(data_per_kpt)
                end += rel_end
        # arrived at the end of the file / block, return what we got
        # SHOW ME WHAT U GOT !!
        return data, len(lines) - 1

    def _extract_data_per_kpt(self, lines):
        self._logger.debug("Starting data extraction for one kpt.")
        # extract eigenvalues for a kpt block
        eigenvalues = []
        block_end = False
        for index, line in enumerate(lines):
            s, i, f = decompose_line(line)
            if len(f) == 0:
                if not block_end:
                    # no data here skip
                    continue
                if block_end:
                    # arrived at next block, return eigenvalues
                    return eigenvalues, index
            block_end = True
            # divide eigenvalue by 2 here because for some reason,
            # it is multiplied by 2 in the ABINIT code.
            eigenvalues.append(f[0] / 2)
        # arrived at the end of the block return what we have
        return eigenvalues, len(lines) - 1

    def _strip_header(self, lines):
        self._logger.debug("Stripping header.")
        for i, line in enumerate(lines):
            if "For each k-point" in line:
                # skip next line also
                return lines[i + 1:], lines[:i + 1]
        # if here, could not strip header
        raise LookupError("Could not strip header from .eig file...")

    def _extract_meta_data(self, header):
        # extract number of kpts and hamiltonian dimensions from the first
        # line.
        # first get the good line
        line = header[1].strip("\n")
        self._logger.debug("Extracting meta data.")
        s, i, f = decompose_line(line)
        self.nkpt = i[2]
        self.nbandtot = i[0]  # number of bands (total)
        self.nspins = i[1]  # number of spins
        self.dmftbandi = i[-2]  # first band considered
        self.dmftbandf = i[-1]  # last band considered
        self.nband = self.dmftbandf - self.dmftbandi + 1
