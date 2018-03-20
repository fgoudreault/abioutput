import numpy as np
import matplotlib.pyplot as plt
from abioutput import EIGParser


HIGH_SYM_PTS = {"FCC": {"L": (0.5, 0.0, 0.0),
                        "Gamma": (0.0, 0.0, 0.0),
                        "X": (0.0, 0.0, 0.5)},
                "none": {"Gamma": (0.0, 0.0, 0.0)},
                "rectangle": {"Gamma": (0.0, 0.0, 0.0),
                              "X": (0.5, 0.0, 0.0),
                              "Y": (0.0, 0.5, 0.0),
                              "M": (0.5, 0.5, 0.0)}}


class Bandstructure:
    """Object that handles band structures given a list of kpts and
    eigenvalues. Can also read directly the eigenvalues from a file using
    the from_file classmethod. In this case, kpts and eigenvalues args
    are directly given to the init method.

    Parameters
    ----------
    kpts : list of kpts
    eigenvalues : list of eigenvalues for each kpt.
    fermi_band : int, optional
                 If not None, gives the band index of the last valence band.
                 Thus, it can compute the fermi energy from the maximum value
                 of that band.
    fermi_energy : float, optional
                   This parameter lets define manually the fermi energy
                   (must be same units as the eigenvalues).
    """
    def __init__(self, kpts, eigenvalues, fermi_band=None, fermi_energy=None):
        self.kpts = kpts
        self.eigenvalues = eigenvalues
        self.bands = self._get_bands(eigenvalues)
        self.fermi_band = fermi_band
        self.fermi_energy = fermi_energy
        if self.fermi_band is not None:
            if self.fermi_energy is None:
                raise ValueError("fermi_energy is already defined.")
            self.fermi_energy = max(self.bands[self.fermi_band])

    def plot(self, bands=None, symmetry="none",
             color="k", save_at=None, show=True,
             other_k_labels=None):
        """Plot the bandstructure.

        Parameters
        ----------
        symmetry: str, optional, {"none", "rectangle", "FCC"}
                  Gives the crystal symmetry of the structure. This will
                  able the labelling of the high symmetry points in the
                  Brillouin Zone.
        color: str, optional
               Gives the line color of the bandstructure. If set to None,
               the color won't be set and it will be a standard multi curve
               pyplot.
        bands: list, optional
               Selects the range of bands to plot (starting from 0).
               If set to None, all bands are shown.
        save_at: str, optional
                 If not None, gives the path to where the figure will be saved.
        show: bool, optional
              If True, the plot will be shown.
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        considered_bands = self.bands
        fermi_energy = self.fermi_energy
        if self.fermi_energy is None:
            fermi_energy = 0
        if bands is not None:
            considered_bands = self.bands[range(bands[0], bands[1] + 1), :]
        for band in considered_bands:
            if color is not None:
                ax.plot(band - fermi_energy, color=color)
            else:
                ax.plot(band - fermi_energy)
        labels, labels_loc = self._get_sym_pts_labels(symmetry)
        ax.set_xticks(labels_loc, labels)
        ax.set_ylabel("Energy")
        if self.fermi_energy:
            ax.set_title(r"$E_F=%f$" % self.fermi_energy)

        if save_at is not None:
            fig.savefig(save_at)
        if show:
            plt.show()

    def _get_sym_pts_labels(self, symmetry):
        labels = []
        labels_loc = []
        high_sym_coordinates = HIGH_SYM_PTS[symmetry]
        for index, kpt in enumerate(self.kpts):
            for label, high_sym_kpt in high_sym_coordinates.items():
                kpt = list(kpt)
                high_sym_kpt = list(high_sym_kpt)
                if kpt == high_sym_kpt:
                    labels_loc.append(index)
                    if label == "Gamma":
                        labels.append(r"$\Gamma$")
                    else:
                        labels.append(label)
                    break
        return labels, labels_loc

    def _get_bands(self, eigenvalues):
        if not isinstance(eigenvalues, np.ndarray):
            eigenvalues = np.array(eigenvalues)

        bands = eigenvalues.T
        return bands

    @classmethod
    def from_file(cls, path, conversion_factor=None, **kwargs):
        """Classmethod to read kpts and eigenvalues directly from an EIG file.

        Parameters
        ----------
        path : The EIG file path.
        conversion_factor : optional, float
                            Multiplies all eigenvalues with this factor.
        """
        eigparser = EIGParser.from_file(path)
        eigs = np.array(eigparser.data["eigenvalues"])
        if conversion_factor is not None:
            eigs *= conversion_factor
        return cls(eigparser.data["coordinates"], eigs, **kwargs)
