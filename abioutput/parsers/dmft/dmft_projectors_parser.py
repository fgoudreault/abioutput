import numpy as np
from ..bases import DataFileParser
from ..utils._common_routines import decompose_line


class DMFTProjectorsParser(DataFileParser):
    """Parser to read projectors files.
    """
    _loggername = "DMFTProjectorsParser"

    def __init__(self, *args, **kwargs):
        """Projectors parser init method.

        Projectors are stored in the `data` attribute as an array of size:

            (nkpt x nband x nspins x natom x norb) of complex numbers

        Parameters
        ----------
        path : str
               The path to the projectors file.
        loglevel : int, optional
                   The logging level.
        """
        super().__init__(*args, **kwargs)
        self.data = self._read_data_from_file(self.filepath)

    def _read_data_from_file(self, path):
        self._logger.info("Extracting data from %s" % path)
        with open(path, 'r') as f:
            lines = f.readlines()

        # DATA IS ORGANIZED AS FOLLOWS:
        # HEADER
        # ikpt = 1
        #  iband = 25
        #      1 1 1  realvalue imvalue
        #      1 1 1  realvalue imvalue
        #      ...
        #  iband = 26...

        # first extract header
        body, header = self._extract_header(lines)
        self.nband = self._get_nband(header)
        data = self._extract_data(body)
        return self._reshape_data(data)

    def _reshape_data(self, data):
        self._logger.info("Reshaping data.")
        # reshape data into an array with size:
        # nkpt x nband x nspins x natom x norb
        data = np.array(data)
        nkpt = len(data)
        nband = len(data[0])
        # find nspins
        allspins_indices = data[:, :, :, 0]
        nspin = len(np.unique(allspins_indices))
        # find natom
        allatom_indices = data[:, :, :, 1]
        natom = len(np.unique(allatom_indices))
        # find norb
        norb = len(np.unique(data[:, :, :, 2]))
        # reshape data
        self._logger.debug("Reshaping to nkpt x nband x nspin x naton x norb ="
                           " %i x %i x %i x %i x %i" %
                           (nkpt, nband, nspin, natom, norb))
        final = np.zeros((nkpt, nband, nspin, natom, norb), dtype=complex)
        # here we drop the spin, atom and orbital indices as they are not
        # important (just arbitrary labels)
        # TODO: consider if those indices are useful to be kept.
        for ik, kpt_block in enumerate(data):
            for ib, band in enumerate(kpt_block):
                for s in range(nspin):
                    for a in range(natom):
                        for o in range(norb):
                            re = band[s * norb * natom + a * norb + o][-2]
                            im = band[s * norb * natom + a * norb + o][-1]
                            final[ik, ib, s, a, o] = re + 1j * im
        self._logger.debug("Reshaping done.")
        return final

    def _get_nband(self, header):
        self._logger.info("Extracting number of bands for checkups.")
        # get total number of bands
        dataline = header[-1]
        s, i, f = decompose_line(dataline)
        return i[1] - i[0] + 1

    def _extract_header(self, lines):
        self._logger.info("Extracting header from file.")
        # return data lines separated from header
        for i, line in enumerate(lines):
            if "ikpt" in line:
                return lines[i:], lines[:i]
        raise LookupError("Could not separate header...")

    def _extract_data(self, lines):
        self._logger.info("Starting data extraction.")
        data = []
        end = 0
        for i, line in enumerate(lines):
            if i < end:
                continue
            if "ikpt" in line:
                # start of kpt block
                kptdata, adv = self._extract_data_from_kpt_block(lines[i:])
                # check that we received correct number of bands
                if len(kptdata) != self.nband:
                    raise ValueError("Was expecting %i bands but read %i"
                                     " instead" % (len(kptdata), self.nband))
                data.append(kptdata)
                end += adv
        return data

    def _extract_data_from_kpt_block(self, lines):
        self._logger.debug("Extracting data from a kpt block.")
        data = []
        end = 0
        block_end = False
        for i, line in enumerate(lines):
            if i < end:
                continue
            if "iband" in line:
                (banddata,
                 adv) = self._extract_data_from_band_block(lines[i:])
                data.append(banddata)
                end += adv
            if "ikpt" in line:
                if not block_end:
                    block_end = True
                else:
                    # arrived at the end of kpt block
                    return data, i
        # arrived at the end of file
        return data, len(lines) - 1

    def _extract_data_from_band_block(self, lines):
        self._logger.debug("Extracting data from a band block.")
        data = []
        block_end = False
        for i, line in enumerate(lines):
            if "iband" in line:
                if block_end:
                    return data, i
                else:
                    block_end = True
            elif "ikpt" in line:
                # end of block
                return data, i
            else:
                # line containing data
                # since we do not know how many orbitals/atoms/spins
                # there are, just
                # gather data until end of block as a huge table
                s, i, f = decompose_line(line)
                data.append(i + f)
                block_end = True
        # arrived at the end of file
        return data, len(lines) - 1
