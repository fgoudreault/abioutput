from .base import BaseSubParser
from .._common_routines import decompose_line
import logging


class EIGParser(BaseSubParser):
    trigger = "Eigenvalues"
    _loggerName = "EIGParser"
    subject = "eigenvalues"

    def __init__(self, lines, loglevel=logging.INFO, check_loi=True):
        super().__init__(loglevel=loglevel)
        self._logger.debug("##########  GETTING EIGENVALUES  #########\n")
        # if check_loi, find the ending of the loi
        if check_loi:
            loi = self._get_loi(lines)
        else:  # consider all the lines (like from an EIG file)
            loi = lines
            self._ending_relative_index = len(lines) - 1
        self.data = None
        if loi is not None:
            self.data = self._get_data(loi)
        self._logger.debug("Eigenvalues done.")

    def _get_loi(self, lines):
        for i, line in enumerate(lines):
            if not len(line) or "Total charge density" in line:
                # end eigenvalues section with first empy line
                # or if right after eigenvalues there is densities
                self._ending_relative_index = i
                return lines[:i]
        # if we are here return all the lines
        self._ending_relative_index = len(lines) - 1
        return lines

    def _get_data(self, lines):
        # get eigenvalues data
        # DATA can be spin polarized, we must separate the cases
        # we can check if data is polarized if SPIN is in the first line
        if "SPIN" in lines[0]:
            # data is polarized
            return self._get_polarized_data(lines)
        # not polarized return data
        return self._get_eigs(lines)

    def _get_polarized_data(self, lines):
        # data is polarized, we need to find the sections for each polarization
        spins = []
        starts = []
        data = {}
        for i, line in enumerate(lines):
            if "SPIN" in line:
                # which spin?
                spins.append(line.split(" ")[-1][:-1].lower())  # down or up
                starts.append(i)
        starts.append(len(lines))
        for n, (start, spin) in enumerate(zip(starts[:-1], spins)):
            data[spin] = self._get_eigs(lines[start:starts[n + 1]])
        return data

    def _get_eigs(self, lines):
        # get eigenvalues data
        data = []
        # units in first line inside parenthesis
        splitted = lines[0].split("(")[1].split(")")[0].split(" ")
        units = list(filter(lambda x: x != "", splitted))[0]
        loi = lines[1:]
        for i, line in enumerate(loi):
            if line.startswith("kpt#"):
                nextline = i + 1
                eigs = []
                # get kpt coordinates
                splitted = line.split(" ")
                filtered = list(filter(lambda xx: xx != '', splitted))
                coord = [float(filtered[-5]),
                         float(filtered[-4]),
                         float(filtered[-3])]

                # get eigenvalues for this kpt
                while not ("kpt#" in loi[nextline] or
                           "occupation numbers" in loi[nextline]):
                    s, i, f = decompose_line(loi[nextline])
                    eigs.extend(f)
                    nextline += 1
                    if nextline == len(loi):
                        # reached the end of eigenvalues
                        break
                if not len(eigs):
                    self._logger.debug("No eigenvalues found for coord: %s" %
                                       str(coord))
                kpt = {"coordinates": coord,
                       "eigenvalues": eigs,
                       "nband": len(eigs),
                       "units": units}
                data.append(kpt)
            if "occupation numbers" in line:
                # occupation numbers are specified inside the eigenvalues
                # we need to append this info to the last kpt dict
                nextline = i + 1
                occupations = []
                while "kpt# " not in loi[nextline]:
                    s, i, f = decompose_line(loi[nextline])
                    occupations.extend(f)
                    nextline += 1
                    if nextline == len(loi):
                        # we reached the end of the lines
                        break
                data[-1]["occupation"] = occupations
        return data

    @classmethod
    def from_file(cls, path):
        """Get the eigenvalues from an EIG file.
        """
        with open(path, "r") as f:
            lines = f.readlines()
        # preprocess lines
        lines = cls.preprocess_lines(lines)
        return cls(lines)
