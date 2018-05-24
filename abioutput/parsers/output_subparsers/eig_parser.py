from .base import BaseSubParser
from ..utils._common_routines import decompose_line
import logging


class EIGParser(BaseSubParser):
    trigger = "Eigenvalues"
    _loggerName = "EIGParser"
    subject = "eigenvalues"

    def __init__(self, lines, loglevel=logging.INFO, check_loi=True):
        """Normally called from the AbinitOutput class but can also be called
        directly onto an EIG file with the from_file classmethod.
        """
        super().__init__(loglevel=loglevel)
        self._logger.debug("\n##########  GETTING EIGENVALUES  #########")
        # if check_loi, find the ending of the loi
        if check_loi:
            loi = self._get_loi(lines)
        else:  # consider all the lines (like from an EIG file)
            loi = lines
            self._ending_relative_index = len(lines) - 1
        self.data = None
        if loi is not None:
            self._logger.debug("%i eigenvalues line to parse." % len(loi))
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
        data = {"coordinates": [],
                "eigenvalues": [],
                "occupations": [],
                "nbands": None,
                "units": None}
        # units in first line inside parenthesis
        splitted = lines[0].split("(")[1].split(")")[0].split(" ")
        units = list(filter(lambda x: x != "", splitted))[0]
        data["units"] = units
        loi = lines[1:]

        # get eigenvalues
        nlines = len(loi)
        lines_for_10percent = nlines // 10
        if lines_for_10percent == 0:
            lines_for_10percent = 1
        skip = 0

        for i, line in enumerate(loi):
            if not i % lines_for_10percent:
                self._logger.debug("EIG progression : %.1f / 100" %
                                   (i / nlines * 100))
            if i < skip:
                continue
            if line.startswith("kpt#"):
                coord = self._get_kpt_coord(line)
                data["coordinates"].append(coord)
                block = self._get_next_number_block(loi[i + 1:])
                eigs = self._get_data_from_block(block)
                data["eigenvalues"].append(eigs)

                skip = i + len(block) + 1
                if not len(eigs):
                    self._logger.debug("No eigenvalues found for coord: %s" %
                                       str(coord))
            elif "occupation numbers" in line:
                # occupation numbers are specified inside the eigenvalues
                # we need to append this info to the last kpt dict
                block = self._get_next_number_block(loi[i + 1:])
                data["occupations"].append(self._get_data_from_block(block))
                skip = i + len(block) + 1
        data["nbands"] = len(data["eigenvalues"][0])
        return data

    def _get_data_from_block(self, block):
        data = []
        for line in block:
            s, i, f = decompose_line(line)
            data.extend(f)
        return data

    def _get_next_number_block(self, loi):
        # get next eigenvalues block
        for i, line in enumerate(loi):
            if "kpt#" in line or "occupation numbers" in line:
                return loi[:i]
        # if at the end, return the whole thing
        return loi

    def _get_kpt_coord(self, line):
            # get kpt coordinates
            splitted = line.split(" ")
            filtered = list(filter(lambda xx: xx != '', splitted))
            return [float(filtered[-5]),
                    float(filtered[-4]),
                    float(filtered[-3])]

    @classmethod
    def from_file(cls, path):
        """Get the eigenvalues from an EIG file.
        """
        with open(path, "r") as f:
            lines = f.readlines()
        # preprocess lines
        lines = cls.preprocess_lines(lines)
        return cls(lines, check_loi=False)
