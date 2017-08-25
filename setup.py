from setuptools import setup
import pip


install_requires = ["abipy", ]

# check if abipy is installed
try:
    abipyexists = True
    import abipy  # noqa
except ImportError:
    abipyexists = False
    print("Abipy is not installed: preparing its installation...")
    # abipy is not installed => install it
    # to install abipy we need to install all those packages manually using pip
    for module in ("numpy", "matplotlib", "netcdf4",
                   "pandas", "pymatgen", "scipy"):
        pip.main(["install", module])

setup(name="abioutput",
      description="Python package to ease reading abinit output using abipy.",
      install_requires=install_requires)

if not abipyexists:
    print("Abipy has been installed and needs the manager.yml"
          " and scheduler.yml files. See Abipy's docs.")
