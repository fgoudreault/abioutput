import numpy as np
import matplotlib.pyplot as plt


HIGH_SYM_PTS = {"FCC": {"L": (0.5, 0.0, 0.0),
                        "Gamma": (0.0, 0.0, 0.0),
                        "X": (0.0, 0.0, 0.5)},
                "none": {"Gamma": (0.0, 0.0, 0.0)},
                "rectangle": {"Gamma": (0.0, 0.0, 0.0),
                              "X": (0.5, 0.0, 0.0),
                              "Y": (0.0, 0.5, 0.0),
                              "M": (0.5, 0.5, 0.0)}}


class Bandstructure:
    def __init__(self, kpts, eigenvalues, fermi_band=None):
        self.kpts = kpts
        self.eigenvalues = eigenvalues
        self.bands = self._get_bands(eigenvalues)
        self.fermi_band = int(fermi_band)
        self.fermi_energy = 0
        if self.fermi_band is not None:
            self.fermi_energy = max(self.bands[self.fermi_band])

    def plot(self, symmetry="none", color="k", save_at=None, show=True):
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
        save_at: str, optional
                 If not None, gives the path to where the figure will be saved.
        show: bool, optional
              If True, the plot will be shown.
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for band in self.bands:
            if color is not None:
                ax.plot(band - self.fermi_energy, color=color)
            else:
                ax.plot(band)
        labels, labels_loc = self._get_sym_pts_labels(symmetry)
        ax.set_xticks(labels_loc, labels)
        ax.set_ylabel("Energy")

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
        return bands.tolist()
