import numpy as np
import matplotlib.pyplot as plt


class Plot:
    """Class to plot something.
    """
    def __init__(self, xdata, ydata, xlabel="", ylabel="", title="",
                 horizontal_lines=None, vertical_lines=None, color="k",
                 linestyle="-",
                 xticks_labels=None, curve_labels=None):
        """Init method.

        Parameters
        ----------
        xdata : list
                The data for the x axis, must be commensurate with ydata.
                Can be a list of xdata for each ydata.
        ydata : list
                The data for the y axis, must be commensurate with xdata.
                Can be 2 dimensional for which each item will be an
                individual curve.
        xlabel,ylabel,title : str, optional
        horizontal_lines : list, optional
                           List of y coordinates to draw a horizontal line.
        vertical_lines : list, optional
                         Same as horizontal_lines but for vertical lines.
        linestyle : str, optional
                    A list of linestyle for each curve. If only one str is
                    used, the same linestyle will be applied to each curve.
        color : str, list, optional
                If only a string, all curves (if many) will be set to this
                color. If a list, must be commensurate with the number of
                curves to draw.
        xticks_labels : list, optional
                        A list of tuple of the form (tick location, tick lavel)
                        If None, no modification on the ticks is done from
                        default matplotlib behavior.
        curve_labels : list, optional
                       The list of curve labels. If a curve label is None,
                       it is not shown.
        """
        # set the attributes of the figure and the curves
        self._fig = None
        self.xdata = self._set_data(xdata)
        self.ydata = self._set_data(ydata)
        n_curves = len(self.ydata)
        # if only one xdata, use the same for all ydata curves
        if len(self.xdata) == 1 and n_curves > 1:
            self.xdata = [self.xdata[0]] * n_curves
        # check that number of xdata matches number of ydata
        if len(self.xdata) != n_curves:
            raise ValueError("Number of x data not equivalent to number of y.")
        # check that all curves are ready to be drawn
        for xdata, ydata in zip(self.xdata, self.ydata):
            assert len(xdata) == len(ydata)

        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title
        self.horizontal_lines = horizontal_lines
        self.vertical_lines = vertical_lines
        if self.horizontal_lines is None:
            self.horizontal_lines = []
        if self.vertical_lines is None:
            self.vertical_lines = []
        self.colors = self._set_curve_attribute(color, n_curves)
        self.linestyles = self._set_curve_attribute(linestyle, n_curves)
        self.xticks_labels = xticks_labels
        self.curve_labels = self._set_curve_labels(curve_labels, n_curves)
        self._fig = None

    def _set_data(self, data):
        # if only one dimension to data, make a list with only one curve
        if len(np.shape(data)) == 1:
            return [data, ]
        # if more than 2 dimensions, raise error
        if len(np.shape(data)) > 2:
            raise TypeError("data is greater than 2D!")
        # else return data
        return data

    def _set_curve_attribute(self, attribute, n_curves):
        # if attribute is only one str, apply same string to all curves
        if isinstance(attribute, str):
            return [attribute] * n_curves
        # if not a str, its a list and it must be the same length as n_curves
        if len(attribute) != n_curves:
            raise ValueError("Number of curve attribute does not match the"
                             " number of curves.")
        # else, return the attribute
        return attribute

    def _set_curve_labels(self, curve_labels, n_curves):
        # curve labels must be matched manually (e.g. for bandstructure we
        # do not want one curve label for each band)
        # if only one string, only the first curve has this label
        if isinstance(curve_labels, str):
            return [curve_labels] + [None] * (n_curves - 1)
        # if None, return a list of Nones
        if curve_labels is None:
            return [None] * n_curves
        # if a list but is not the same length as n_curves
        if len(curve_labels) != n_curves:
            raise ValueError("Number of labels does not match"
                             " number of curves.")
        # else, return the list of curve_labels
        return curve_labels

    def __add__(self, plot):
        """Method that allows the addition of two plots.

        The addition is defined as another plot with the same characteritics
        but the superposition of all curves.
        """
        if self.xlabel != plot.xlabel or self.ylabel != plot.ylabel:
            raise ValueError("Axis labels does not match :(")
        all_xs = np.concatenate([self.xdata, plot.xdata])
        all_ys = np.concatenate([self.ydata, plot.ydata])
        all_hor_lines = np.concatenate([self.horizontal_lines,
                                       plot.horizontal_lines])
        all_ver_lines = np.concatenate([self.vertical_lines,
                                       plot.vertical_lines])
        allcolors = np.concatenate([self.colors, plot.colors])
        allcurvelabels = np.concatenate([self.curve_labels, plot.curve_labels])
        alllinestyles = np.concatenate([self.linestyles, plot.linestyles])
        # xticks labels, only keep those that are different
        all_xticks = list(self.xticks_labels)
        for xtick in plot.xticks_labels:
            if xtick not in all_xticks:
                all_xticks.append(xtick)
        # compute new title
        if self.title == "" and plot.title != "":
            title = plot.title
        elif self.title != "" and plot.title == "":
            title = self.title
        elif self.title == "" and plot.title == "":
            title = ""
        else:
            title = self.title + " + " + plot.title
        return Plot(all_xs, all_ys,
                    xlabel=self.xlabel,
                    ylabel=self.ylabel,
                    title=title,
                    horizontal_lines=all_hor_lines,
                    vertical_lines=all_ver_lines,
                    linestyle=alllinestyles,
                    color=allcolors,
                    xticks_labels=all_xticks,
                    curve_labels=allcurvelabels)

    def plot(self,
             show_legend=True,
             legend_outside=True,
             vertical_linestyle="--",
             horizontal_linestyle="--",
             vertical_color="k",
             horizontal_color="k"):
        """Method to plot the figure.

        Parameters
        ----------
        show_legend : bool, optional
                      If True, the legend is shown.
        legend_outside : bool, optional
                         If True, the legend (if displayed) will be drawn
                         outside graph.
        vertical_linestyle : str, optional
                             Gives the linestyle for vertical lines.
        horizontal_linestyle : str, optional
                               Gives the linestyle for horizontal lines.
        vertical_color : str, optional
                         Gives the vertical line color.
        horizontal_color : str, optional
                           Gives the horizontal line color.
        """
        self._fig = plt.figure()
        ax = self._fig.add_subplot(111)
        for xdata, curve, color, linestyle, label in zip(self.xdata,
                                                         self.ydata,
                                                         self.colors,
                                                         self.linestyles,
                                                         self.curve_labels):
            ax.plot(xdata, curve, color=color, linestyle=linestyle,
                    label=label)
        for hline in self.horizontal_lines:
            ax.axhline(hline, color=horizontal_color,
                       linestyle=horizontal_linestyle)
        for vline in self.vertical_lines:
            ax.axvline(vline, color=vertical_color,
                       linestyle=vertical_linestyle)
        if self.xticks_labels is not None:
            ticks_loc = [x[0] for x in self.xticks_labels]
            ticks_labels = [x[1] for x in self.xticks_labels]
            ax.set_xticks(ticks_loc)
            ax.set_xticklabels(ticks_labels)
        # set title
        ax.set_title(self.title)
        # show legend if needed and if at least one curve_labels is not None
        if show_legend and not all([True if x is None else False
                                    for x in self.curve_labels]):
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
