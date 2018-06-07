import abc
import matplotlib.pyplot as plt
import numpy as np


class Plot:
    """Class to plot something.
    """
    def __init__(self):
        """Init method.
        """
        # init the attributes of the figure and the curves
        self._fig = None
        self._curves = []
        self._xtick_labels = None
        self._vlines = []
        self._hlines = []

        self._xlabel = ""
        self._ylabel = ""
        self._title = ""

    @property
    def xlabel(self):
        return self._xlabel

    @xlabel.setter
    def xlabel(self, label):
        if not isinstance(label, str):
            raise TypeError("Label must be str.")
        self._xlabel = label

    @property
    def ylabel(self):
        return self._ylabel

    @ylabel.setter
    def ylabel(self, label):
        if not isinstance(label, str):
            raise TypeError("Label must be str.")
        self._ylabel = label

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        if not isinstance(title, str):
            raise TypeError("Title must be str.")
        self._title = title

    @property
    def xtick_labels(self):
        return self._xtick_labels

    @xtick_labels.setter
    def xtick_labels(self, labels):
        # must be a list of two component lists.
        if type(labels) not in (list, tuple):
            raise TypeError("Labels should be a list.")
        if type(labels[0]) not in (list, tuple) or len(labels[0]) != 2:
            raise TypeError("Each xtick_labels componant is a list of"
                            " (pos, label).")
        self._xtick_labels = labels

    def add_curve(self, *args, **kwargs):
        """Add a curve to the plot.

        All parameters are passed to the Curve class.
        """
        self._curves.append(Curve(*args, **kwargs))

    def add_vline(self, *args, **kwargs):
        """Add a vertical line.

        All parameters are passed to the VLine class.
        """
        self._vlines.append(VLine(*args, **kwargs))

    def add_hline(self, *args, **kwargs):
        """Add a horizontal line.

        All parameters are passed to the HLine class.
        """
        self._hlines.append(HLine(*args, **kwargs))

    def set_curve_label(self, label, curve_index):
        """Set the label of a specific curve.

        Parameters
        ----------
        label : str
                The label to apply to the curve.
        curve_index : int
                      The curve index.
        """
        self._curves[curve_index].label = label

    def __add__(self, plot):
        """Method that allows the addition of two plots.

        The addition is defined as another plot with the same characteritics
        but the superposition of all curves.
        """
        if self.xlabel != plot.xlabel or self.ylabel != plot.ylabel:
            raise ValueError("Axis labels does not match :(")
        newplot = Plot()
        for attr in ("_curves", "_hlines", "_vlines"):
            setattr(newplot, attr, getattr(self, attr) + getattr(plot, attr))
        all_xticks = list(self.xtick_labels)
        for xtick in plot.xtick_labels:
            if xtick not in all_xticks:
                all_xticks.append(xtick)
        newplot.xtick_labels = all_xticks
        # compute new title
        if self.title == "" and plot.title != "":
            title = plot.title
        elif self.title != "" and plot.title == "":
            title = self.title
        elif self.title == "" and plot.title == "":
            title = ""
        else:
            title = self.title + " + " + plot.title
        newplot.title = title
        return newplot

    def plot(self,
             show_legend=True,
             legend_outside=True):
        """Method to plot the figure.

        Parameters
        ----------
        show_legend : bool, optional
                      If True, the legend is shown.
        legend_outside : bool, optional
                         If True, the legend (if displayed) will be drawn
                         outside graph.
        """
        self._fig = plt.figure()
        ax = self._fig.add_subplot(111)
        # plot curves and lines
        for curve in self._curves:
            curve.plot_on_axis(ax)
        for hline in self._hlines:
            hline.plot_on_axis(ax)
        for vline in self._vlines:
            vline.plot_on_axis(ax)
        # set ticks
        if self.xtick_labels is not None:
            ticks_loc = [x[0] for x in self.xtick_labels]
            ticks_labels = [x[1] for x in self.xtick_labels]
            ax.set_xticks(ticks_loc)
            ax.set_xticklabels(ticks_labels)
        # set title and axis labels
        ax.set_title(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        # show legend if needed and if at least one curve_labels is not None
        all_labels = [c.label for c in self._curves]
        if show_legend and not all([True if x is None else False
                                    for x in all_labels]):
            if legend_outside:
                ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
            else:
                ax.legend(loc="best")
        plt.show()

    def save(self, path):
        if self._fig is None:
            raise ValueError("Use the plot method to generate figure.")
        self._fig.savefig(path)

    def reset(self):
        del self._fig
        self._fig = None


class Curve:
    """Class that represents a curve."""

    def __init__(self, xdata, ydata, linestyle="-", color="k", label=None):
        """Curve init method.

        Parameters
        ----------
        x_data : array-like
                 x-data points.
        y_data : array-like
                 y-data points.
        linestyle : str, optional
                    Curve linestyle.
        color : str, optional
                Curve color.
        label : str, optional
                Curve label. None = no label.
        """
        self.xdata = self._check_list(xdata)
        self.ydata = self._check_list(ydata)
        if len(self.xdata) != len(self.ydata):
            raise ValueError("xdata and ydata must be same length!")
        self.linestyle = linestyle
        self.color = color
        self.label = label

    def _check_list(self, data):
        # check if arguments are array-like and return numpy arrays
        if type(data) not in (np.ndarray, list, tuple):
            raise TypeError("Argument should be array-like.")
        if isinstance(data, np.ndarray):
            if len(data.shape) >= 2:
                raise TypeError("Argument is > 1D data!")
        return np.array(data)

    def plot_on_axis(self, axis):
        axis.plot(self.xdata,
                  self.ydata,
                  linestyle=self.linestyle,
                  color=self.color,
                  label=self.label)


class StraightLine(abc.ABC):
    def __init__(self, pos, linestyle="-", color="k"):
        self.position = pos
        self.linestyle = linestyle
        self.color = color

    @abc.abstractmethod
    def plot_on_axis(self, *args, **kwargs):
        pass


class VLine(StraightLine):
    def plot_on_axis(self, axis):
        axis.axvline(self.position,
                     linestyle=self.linestyle,
                     color=self.color)


class HLine(StraightLine):
    def plot_on_axis(self, axis):
        axis.axhline(self.position,
                     linestyle=self.linestyle,
                     color=self.color)
