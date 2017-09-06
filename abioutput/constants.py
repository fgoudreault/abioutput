from pint import UnitRegistry
from numpy import pi


ureg = UnitRegistry()


c = 299792458 * ureg.meters / ureg.second
G = 6.67408e-11 * ureg.meters ** 3 / ureg.kilogram / ureg.seconds ** 2
h = 6.626070040e-34 * ureg.joules * ureg.seconds
e = 1.6021766208e-19 * ureg.coulomb
m_e = 9.10938356e-31 * ureg.kilogram
k_B = 1.38064852e-23 * ureg.joules / ureg.kelvin
amu = 1.66053904e-27 * ureg.kilogram
hbar = h / (2 * pi)
mu_0 = 4 * pi * 10 ** (-7) * ureg.newton / ureg.ampere ** 2
epsilon_0 = 1 / (mu_0 * c ** 2)
mu_B = e * hbar / (2 * m_e)
FINE_STRUCTURE_CONSTANT = mu_0 * e ** 2 * c / (2 * h)
RYDBERG = FINE_STRUCTURE_CONSTANT ** 2 * m_e * c / (2 * h)
BOHR_RADIUS = FINE_STRUCTURE_CONSTANT / (4 * pi * RYDBERG)
