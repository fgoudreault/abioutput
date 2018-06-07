from abioutput import Bandstructure


path = "GaAs_no_SO_EIG"
fermi_band=3
b = Bandstructure.from_file(path,
                            fermi_band=fermi_band)
plot1 = b.plot(ylabel="E (eV)")
plot1.set_curve_label("No SO", 0)

path = "GaAs_SO_EIG"
fermi_band=7
b2 = Bandstructure.from_file(path,
                             fermi_band=fermi_band)
plot2 = b2.plot(ylabel="E (eV)", color="b")
plot2.set_curve_label("with SO", 0)

plot3 = plot1 + plot2
plot3 = plot3.plot()
