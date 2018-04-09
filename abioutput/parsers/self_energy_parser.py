import matplotlib.pyplot as plt
import numpy as np


def plot_self_energy(selfparsers,
                     xlabel=r"Matsubara frequencies $\omega_n$",
                     ylabel_re=r"$\Re(\Sigma(\omega_n))$",
                     ylabel_im=r"$\Im(\Sigma(\omega_n))$",
                     labels=None,
                     with_renorm_factor=True):
        """Plot the self energy from one or many self energy parsers.

        Parameters
        ----------
        selfparser : list
                     The list of self energy parsers.
        xlabel : str, optional
                 Gives the label for the x axis (usally matsubara freqs).
        ylabel_re : str, optional
                    Gives the label for the real part of the self energy.
        ylabel_im : str, optional
                    Gives the label for the imaginary part of the self energy.
        labels : list, optional
                 If not None, gives the label
                 (only shown in the real part pane)
                 of the curve (if many curves).
        with_renorm_factor : bool, optional
                             If True, the mass renormalization factor is
                             added in the label.
        """
        showlegend = True
        if isinstance(selfparsers, SelfEnergyParser):
            selfparsers = (selfparsers, )
        if labels is None:
            showlegend = False
            labels = [None] * len(selfparsers)
        fig = plt.figure()
        axRe = fig.add_subplot(211)
        axRe.set_ylabel(ylabel_re)

        axIm = fig.add_subplot(212)
        axIm.set_ylabel(ylabel_im)
        axIm.set_xlabel(xlabel)
        for self, label in zip(selfparsers, labels):
            if with_renorm_factor:
                showlegend = True
                if label is None:
                    label = r""
                label += r" $Z^{-1}$=%.2f" % self.mass_renormalization_factor()
            axRe.plot(self.data["frequencies"], self.data["real"], label=label)
            axIm.plot(self.data["frequencies"], self.data["imaginary"])
        if showlegend:
            axRe.legend(loc="best")


class SelfEnergyParser:
    def __init__(self, path, many_self_option="mean", dc=0):

        if isinstance(path, str):
            # only one path, just extract data
            self.data = self._extract_data(path, dc=dc)
        else:
            # list like
            self.data = self._get_data_from_multiple_srcs(path,
                                                          many_self_option,
                                                          dc=dc)

    def plot(self, label=None, **kwargs):
        """Plot the self energy.

        Parameters
        ----------
        xlabel : str, optional
                 Gives the label for the x axis (usally matsubara freqs).
        ylabel_re : str, optional
                    Gives the label for the real part of the self energy.
        ylabel_im : str, optional
                    Gives the label for the imaginary part of the self energy.
        label : list, optional
                If not None, gives the label
                (only shown in the real part pane)
                of the curve (if many curves).
        with_renorm_factor : bool, optional
                             If True, the mass renormalization factor is
                             added in the label.
        """
        plot_self_energy((self, ), labels=(label, ), **kwargs)

    def _extract_data(self, path, dc=0):
        d = np.loadtxt(path)
        return {"frequencies": d[:, 0],
                "real": d[:, 1] - dc,
                "imaginary": d[:, 2]}

    def _get_data_from_multiple_srcs(self, paths, many_self_option, **kwargs):
        allopts = ("mean", )
        listtypes = (tuple, np.ndarray, list)
        if many_self_option not in allopts:
            raise ValueError("%s not a valid options from %s." %
                             (many_self_option, str(allopts)))
        if type(paths) not in listtypes:
            raise ValueError("The paths given should be in a list.")

        # get all data
        datas = [self._extract_data(path, **kwargs) for path in paths]
        if many_self_option == "mean":
            # combine all results into a single mean option
            return self._get_self_mean(datas)

    def _get_self_mean(self, datas):
        final_data = {}
        # check that each self energy function is defined on the same
        # frequency grid
        freqs = datas[0]["frequencies"]
        for data in datas[1:]:
            f = data["frequencies"]
            if not all(freqs == f):
                raise ValueError("Not all self energy files are defined"
                                 " on the same frequency grid!")
        final_data["frequencies"] = freqs
        # compute the mean on all frequencies
        todo = ("real", "imaginary")
        for component in todo:
            comp_matrix = np.array([d[component] for d in datas])
            final_data[component] = np.mean(comp_matrix, axis=0)
        return final_data

    def mass_renormalization_factor(self, polynomial_degree=4,
                                    n_frequencies=6,
                                    polynomial=True,
                                    print_coeffs=False):
        """Compute the mass normalization factor from the imaginary part
        of the self energy by fitting a 4th degree polynomial.

        Parameters
        ----------
        polynomial : bool, optional
                     If True, a polynomial of degree given by the
                     polynomial_degree parameter over the n_frequencies first
                     matsubara frequencies. If False, the slope is given
                     by a finite difference formula.
        polynomial_degree : int, optional
                            Gives the degree of the fitted polynomial if
                            polynomial is True.
        n_frequencies : int, optional
                        Gives the number of frequencies to consider in case
                        of a polynomial fit (if polynomial is True).
        print_coeffs : bool, optional
                       If True, the polynomial coefficients will be printed
                       when polynomial is True.
        """
        selfenergy = self.data["imaginary"]
        freqs = self.data["frequencies"]
        if polynomial:
            # do the fit only on the first 6 numbers
            poly_coeffs = np.polyfit(freqs[:n_frequencies],
                                     selfenergy[:n_frequencies],
                                     polynomial_degree)
            # the slope at 0 equals the linear part of the fit
            slope = poly_coeffs[-2]
            if print_coeffs:
                print("Polynomial coefficients in order of the biggest"
                      " power to the least. ")
                print(poly_coeffs)
        else:
            slope = selfenergy[0] / freqs[0]
        # the renorm factor is 1 / (1 - slope at 0)
        return 1 - slope
