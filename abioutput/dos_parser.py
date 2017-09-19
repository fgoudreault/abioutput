import numpy as np


class DOSParser:
    def __init__(self, path):
        self.data, self.titles = self._get_data_from_file(path)

    def _get_data_from_file(self, path):
        # this is a numpy array with the data.
        data = np.loadtxt(path)
        # we now need the columns title
        titles = self._get_titles(path)
        return data, titles

    def _get_titles(self, path):
        with open(path) as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if not line.startswith("#"):
                titleindex = i - 1
                while "energy" not in lines[titleindex]:
                    titleindex -= 1
                    if titleindex <= 0:
                        raise LookupError("Could not find the title line!")
                titlesline = lines[titleindex].strip("\n").strip("#")
                # titlesline2 = lines[i - 1]
                break
        else:
            raise LookupError("There is only comments in this file!")
        # titlesline looks like this:
        #  #        energy        DOS       Integr. DOS      DOS         DOS
        # i'm not quite sure how could I efficiently get all titles since
        # this line could change depending of the input options.
        # for now, just return it knowing the first column is the energy
        # and the second the total DOS.
        return titlesline
