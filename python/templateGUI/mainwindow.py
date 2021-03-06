__author__ = 'alefur'

from datetime import datetime as dt
from functools import partial

from PyQt5.QtWidgets import QGridLayout, QWidget, QGroupBox, QLineEdit, QPushButton, QPlainTextEdit, QVBoxLayout, \
    QHBoxLayout

from PyQt5.QtGui import QFont, QTextCursor

from widgets import ValueGB
from graph import Graph, Curve


class LogArea(QPlainTextEdit):
    def __init__(self):
        QPlainTextEdit.__init__(self)
        self.logArea = QPlainTextEdit()
        self.setMaximumBlockCount(10000)
        self.setReadOnly(True)

        self.setStyleSheet("background-color: black;color:white;")
        self.setFont(QFont("Monospace", 8))

    def newLine(self, line):
        self.insertPlainText("\n%s  %s" % (dt.now().strftime("%H:%M:%S.%f"), line))
        self.moveCursor(QTextCursor.End)
        self.ensureCursorVisible()

    def trick(self, qlineedit):
        self.newLine(qlineedit.text())


class Device(QGroupBox):
    def __init__(self, title):
        QGroupBox.__init__(self)
        self.setTitle(title)
        self.grid = QGridLayout()


class Example(QWidget):
    def __init__(self, mainTree):
        QWidget.__init__(self)
        self.mainTree = mainTree
        self.mainLayout = QVBoxLayout()
        self.windowLayout = QHBoxLayout()
        self.labelLayout = QGridLayout()

        self.labelLayout.addWidget(ValueGB('Enabled ', self.actor.models['xcu_r0'], 'ionpump1', 0, '{:g}'), 0, 0)
        self.labelLayout.addWidget(ValueGB('Voltage(V)', self.actor.models['xcu_r0'], 'ionpump1', 1, '{:g}'), 0, 1)
        self.labelLayout.addWidget(ValueGB('Current(A)', self.actor.models['xcu_r0'], 'ionpump1', 2, '{:g}'), 0, 2)
        self.labelLayout.addWidget(ValueGB('Temperature(K)', self.actor.models['xcu_r0'], 'ionpump1', 3, '{:g}'), 0, 3)
        self.labelLayout.addWidget(ValueGB('Pressure(Torr)', self.actor.models['xcu_r0'], 'ionpump1', 4, '{:g}'), 0, 4)

        self.labelLayout.addWidget(ValueGB('Enabled ', self.actor.models['xcu_r0'], 'ionpump2', 0, '{:g}'), 1, 0)
        self.labelLayout.addWidget(ValueGB('Voltage(V)', self.actor.models['xcu_r0'], 'ionpump2', 1, '{:g}'), 1, 1)
        self.labelLayout.addWidget(ValueGB('Current(A)', self.actor.models['xcu_r0'], 'ionpump2', 2, '{:g}'), 1, 2)
        self.labelLayout.addWidget(ValueGB('Temperature(K)', self.actor.models['xcu_r0'], 'ionpump2', 3, '{:g}'), 1, 3)
        self.labelLayout.addWidget(ValueGB('Pressure(Torr)', self.actor.models['xcu_r0'], 'ionpump2', 4, '{:g}'), 1, 4)

        self.labelLayout.addWidget(ValueGB('Cooler_Setpoint(K)', self.actor.models['xcu_r0'], 'coolerTemps', 0, '{:g}'),
                                   2, 0)
        self.labelLayout.addWidget(ValueGB('Cooler_Reject(C)', self.actor.models['xcu_r0'], 'coolerTemps', 1, '{:g}'),
                                   2, 1)
        self.labelLayout.addWidget(ValueGB('Cooler_Tip(K)', self.actor.models['xcu_r0'], 'coolerTemps', 2, '{:g}'), 2,
                                   2)
        self.labelLayout.addWidget(ValueGB('Cooler_Power(W)', self.actor.models['xcu_r0'], 'coolerTemps', 3, '{:g}'), 2,
                                   3)

        self.labelLayout.addWidget(ValueGB('Shutters', self.actor.models['enu'], 'shutters', 2, '{:s}'), 3, 0)

        self.commandLine = QLineEdit()
        self.commandButton = QPushButton('Send Command')
        self.commandButton.clicked.connect(self.sendCmdLine)

        self.logArea = LogArea()

        self.labelLayout.addWidget(self.commandLine, 4, 0, 1, 4)
        self.labelLayout.addWidget(self.commandButton, 4, 4, 1, 1)

        self.labelLayout.addWidget(self.createButton(title='POWER ON', cmdStr='mcs power on'), 5, 0, 1, 1)
        self.labelLayout.addWidget(self.createButton(title='POWER OFF', cmdStr='mcs power off'), 5, 1, 1, 1)



        self.tempGraph = Graph(parent=self)

        self.actor.models['xcu_r0'].keyVarDict["coolerTemps"].addCallback(partial(self.tempGraph.newValue))
        self.actor.models['xcu_r0'].keyVarDict["temps"].addCallback(partial(self.tempGraph.newValue))

        self.tempGraph.addCurve(actor='xcu_r0', keyword="coolerTemps", index=0, label='Cooler_Setpoint', axe=0, ylabel='Temperature(K)')
        self.tempGraph.addCurve(actor='xcu_r0', keyword="coolerTemps", index=2, label='Cooler_Tip', axe=0)
        self.tempGraph.addCurve(actor='xcu_r0', keyword="coolerTemps", index=3, label='Cooler_Power', axe=1, ylabel='Power(W)')
        #
        self.tempGraph.addCurve(actor='xcu_r0', keyword="temps", index=0, label='Detector_Box', axe=0)
        self.tempGraph.addCurve(actor='xcu_r0', keyword="temps", index=3, label='Thermal_Spreader', axe=0)


        self.pressureGraph = Graph(parent=self)

        self.actor.models['xcu_r0'].keyVarDict["pressure"].addCallback(partial(self.pressureGraph.newValue))
        self.actor.models['xcu_r0'].keyVarDict["ionpump1"].addCallback(partial(self.pressureGraph.newValue))
        self.actor.models['xcu_r0'].keyVarDict["ionpump2"].addCallback(partial(self.pressureGraph.newValue))

        self.pressureGraph.addCurve(actor='xcu_r0', keyword="pressure", index=0, label='Ion_Gauge', axe=0, ylabel='Pressure(Torr)', logy=True)
        self.pressureGraph.addCurve(actor='xcu_r0', keyword="ionpump1", index=4, label='Ionpump1', axe=0)
        self.pressureGraph.addCurve(actor='xcu_r0', keyword="ionpump2", index=4, label='Ionpump2', axe=0)


        self.windowLayout.addLayout(self.labelLayout)
        self.windowLayout.addWidget(self.tempGraph)
        self.windowLayout.addWidget(self.pressureGraph)

        self.mainLayout.addLayout(self.windowLayout)
        self.mainLayout.addWidget(self.logArea)
        self.setLayout(self.mainLayout)

    @property
    def actor(self):
        return self.mainTree.actor

    def createButton(self, title, cmdStr):
        button = QPushButton(title)
        button.clicked.connect(partial(self.sendCommand, cmdStr))
        return button

    def sendCmdLine(self):
        self.sendCommand(self.commandLine.text())

    def sendCommand(self, fullCmd):
        import opscore.actor.keyvar as keyvar
        [actor, cmdStr] = fullCmd.split(' ', 1)
        self.logArea.newLine('cmdIn=%s %s' % (actor, cmdStr))
        self.actor.cmdr.bgCall(**dict(actor=actor,
                                      cmdStr=cmdStr,
                                      timeLim=600,
                                      callFunc=self.returnFunc,
                                      callCodes=keyvar.AllCodes))

    def returnFunc(self, cmdVar):
        self.logArea.newLine('cmdOut=%s' % cmdVar.replyList[0].canonical())
        for i in range(len(cmdVar.replyList) - 1):
            self.logArea.newLine(cmdVar.replyList[i + 1].canonical())
