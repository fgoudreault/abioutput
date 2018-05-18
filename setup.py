from setuptools import setup
import pip


install_requires = [  # "abipy",
                    "pint", "colorama", "tabulate"]
# need dev version
abipy_git = ("git+git://github.com/abinit/abipy@develop#egg=abipy")

# check if abipy is installed
try:
    abipyexists = True
    import abipy  # noqa
except (ImportError, ModuleNotFoundError):
    abipyexists = False
    print("Abipy is not installed: preparing its installation...")
    # abipy is not installed => install it
    # to install abipy we need to install all those packages manually using pip
    for module in ("numpy", "matplotlib", "netcdf4",
                   "pandas", "pymatgen", "scipy", "abipy"):
        if module == "abipy":
            module = abipy_git
        pip.main(["install", module])

setup(name="abioutput",
      description="Python package to ease reading abinit output using abipy.",
      install_requires=install_requires,
      )

if not abipyexists:
    print("Abipy has been installed and needs the manager.yml"
          " and scheduler.yml files. See Abipy's docs.")
