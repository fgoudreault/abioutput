import numpy as np


class SpectralParser:
    def __init__(self, path):
        self.data = self._extract_data(path)

    def _extract_data(self, path):
        return np.loadtxt(path)
