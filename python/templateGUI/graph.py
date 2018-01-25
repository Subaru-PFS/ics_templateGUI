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


# plt.style.use('ggplot')


class Graph(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, labels=[], width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.labels = labels
        self.plotActivated = [False for label in labels]
        self.axes = fig.add_subplot(111)

        self.dates = []
        self.vals = []

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot(self, *args, **kwargs):
        self.axes.cla()
        self.axes.plot(*args, **kwargs)
        self.axes.grid()

        self.draw()
        self.axes.set_position([0.2, 0.2, 0.6, 0.6])  #

    def plot_date(self):
        vals = np.array(self.vals)
        self.axes.cla()

        for i in range(len(self.labels)):
            if self.plotActivated[i]:
                self.axes.plot_date(self.dates, vals[:, i], 'o-', label=self.labels[i], markersize=4)
        self.arangeDate()
        self.axes.grid()
        self.axes.legend()
        self.draw()

    def newValue(self, keyvar):
        values = keyvar.getValue(doRaise=False)
        timestamp = epoch2num(keyvar.timestamp)

        values = [value if value is not None else np.nan for value in values]

        if values is not None:
            self.vals.append(values)
            self.dates.append(timestamp)
            self.dates = self.dates[-100:]
            self.vals = self.vals[-100:]

            self.plot_date()

    def arangeDate(self):
        t0, tmax = self.axes.get_xlim()
        if tmax - t0 > 7:
            fmtDate = "%Y-%m-%d"
        elif tmax - t0 > 1:
            fmtDate = "%a %H:%M"
        else:
            fmtDate = "%H:%M:%S"

        self.axes.xaxis.set_major_formatter(DateFormatter(fmtDate))
        plt.setp(self.axes.xaxis.get_majorticklabels(), rotation=45, horizontalalignment='right')
