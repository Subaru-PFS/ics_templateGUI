from __future__ import unicode_literals

import matplotlib
import numpy as np

# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5 import QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import epoch2num, DateFormatter

import matplotlib.pyplot as plt
from matplotlib.ticker import rcParams

rcParams.update({'figure.autolayout': True})

from matplotlib import colors as mcolors

colors = [val for val in dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS).values()]


class Dataset(object):
    def __init__(self, sizeLim=100):
        self.sizeLim = sizeLim
        self.ldates = []
        self.lvals = []

    @property
    def dates(self):
        return np.array(self.ldates)

    @property
    def vals(self):
        return np.array(self.lvals)

    def newData(self, date, vals):
        self.ldates.append(date)
        self.lvals.append(vals)

        self.ldates = self.ldates[-self.sizeLim:]
        self.lvals = self.lvals[-self.sizeLim:]


class Curve(object):
    def __init__(self, graph, actor, keyword, index, label, axe):
        self.graph = graph
        self.actor = actor
        self.keyword = keyword
        self.label = label
        self.index = index
        self.axe = axe

    @property
    def dates(self):
        return self.dataset.dates

    @property
    def vals(self):
        return self.dataset.vals[:, self.index]

    @property
    def dataset(self):
        return self.graph.data[self.actor, self.keyword]


class Graph(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = [fig.add_subplot(111)]

        self.data = {}
        self.curves = []

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    @property
    def ax1(self):
        return self.axes[0]

    def addCurve(self, actor, keyword, index, label, axe, logy=False, ylabel=False):
        curve = Curve(graph=self,
                      actor=actor,
                      keyword=keyword,
                      index=index,
                      label=label,
                      axe=axe)
        try:
            axe = self.axes[curve.axe]
        except IndexError:
            self.axes.append(self.ax1.twinx())
            axe = self.axes[curve.axe]

        if ylabel:
            axe.set_ylabel(ylabel)
        if logy:
            axe.set_yscale('log', basey=10)

        curve.color = colors[len(self.curves)]
        self.curves.append(curve)

    def plot_date(self):
        self.clear()

        for curve in self.curves:
            try:
                self.axes[curve.axe].plot_date(curve.dates, curve.vals,
                                               'o-', color=curve.color, label=curve.label, markersize=4)
            except KeyError:
                print ('dataset not created yet')


        if self.curves:
            try:
                self.addDate()
                self.addLegend()
                self.draw()
            except ValueError:
                pass


    def addLegend(self):
        lns = self.ax1.get_lines()
        for i in range(len(self.axes) - 1):
            lns += self.axes[i + 1].get_lines()

        labs = [line.get_label() for line in lns]

        for axe in self.axes:
            axe.grid()
        self.ax1.legend(lns, labs)

    def newValue(self, keyvar):

        values = keyvar.getValue(doRaise=False)
        timestamp = epoch2num(keyvar.timestamp)
        values = (values,) if type(values) is not tuple else values
        values = tuple([value if value is not None else np.nan for value in values])

        key = keyvar.actor, keyvar.name
        try:
            dataset = self.data[key]
        except KeyError:
            self.data[key] = Dataset()
            dataset = self.data[key]

        dataset.newData(timestamp, values)

        self.plot_date()

    def clear(self):
        ylabels = [ax.get_ylabel() for ax in self.axes]

        for ax, ylabel in zip(self.axes, ylabels):
            ax.cla()
            ax.set_ylabel(ylabel)

    def addDate(self):
        t0, tmax = self.ax1.get_xlim()
        if tmax - t0 > 7:
            fmtDate = "%Y-%m-%d"
        elif tmax - t0 > 1:
            fmtDate = "%a %H:%M"
        else:
            fmtDate = "%H:%M:%S"

        self.ax1.xaxis.set_major_formatter(DateFormatter(fmtDate))
        plt.setp(self.ax1.xaxis.get_majorticklabels(), rotation=45, horizontalalignment='right')
