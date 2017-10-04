import numpy as np


class SelfEnergyParser:
    def __init__(self, path, many_self_option="mean"):
        if isinstance(path, str):
            # only one path, just extract data
            self.data = self._extract_data(path)
        else:
            # list like
            self.data = self._get_data_from_multiple_srcs(path,
                                                          many_self_option)

    def _extract_data(self, path):
        d = np.loadtxt(path)
        return {"frequencies": d[:, 0],
                "real": d[:, 1],
                "imaginary": d[:, 2]}

    def _get_data_from_multiple_srcs(self, paths, many_self_option):
        allopts = ("mean", )
        listtypes = (tuple, np.ndarray, list)
        if many_self_option not in allopts:
            raise ValueError("%s not a valid options from %s." %
                             (many_self_option, str(allopts)))
        if type(paths) not in listtypes:
            raise ValueError("The paths given should be in a list.")

        # get all data
        datas = [self._extract_data(path) for path in paths]
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
