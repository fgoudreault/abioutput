from pint import UnitRegistry
from numpy import pi


ureg = UnitRegistry()


c = 299792458 * ureg.meters / ureg.second  # m/s
G = 6.67408e-11 * ureg.meters ** 3 / ureg.kilogram / ureg.seconds ** 2
h = 6.626070040e-34 * ureg.kilogram * ureg.meter ** 2 / ureg.seconds
e = 1.6021766208e-19 * ureg.coulomb
m_e = 9.10938356e-31 * ureg.kilogram
k_B = 1.38064852e-23 * ureg.kilogram * ureg.meters ** 2 / (ureg.kelvin *
                                                           ureg.seconds ** 2)
amu = 1.66053904e-27 * ureg.kilogram
hbar = h / (2 * pi)
mu_0 = 4 * pi * 10 ** (-7) * ureg.kilogram * ureg.meters / ureg.coulomb ** 2
epsilon_0 = 1 / (mu_0 * c ** 2)
mu_B = e * hbar / (2 * m_e)
FINE_STRUCTURE_CONSTANT = mu_0 * e ** 2 * c / (2 * h)
RYDBERG = FINE_STRUCTURE_CONSTANT ** 2 * m_e * c ** 2 / 2  # Joules
BOHR_RADIUS = FINE_STRUCTURE_CONSTANT / (4 * pi * RYDBERG)

HARTREE_TO_JOULES = 2 * RYDBERG
JOULES_TO_EV = 1 / e
HARTREE_TO_EV = HARTREE_TO_JOULES.m * JOULES_TO_EV.m
HARTREE_TO_KELVIN = HARTREE_TO_JOULES.m / k_B.m
