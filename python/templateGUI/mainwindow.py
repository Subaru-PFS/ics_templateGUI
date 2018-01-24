__author__ = 'alefur'

from datetime import datetime as dt

from PyQt5.QtWidgets import QGridLayout, QWidget, QGroupBox, QLineEdit, QPushButton, QPlainTextEdit
from PyQt5.QtGui import QFont, QTextCursor

from widgets import ValueGB


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
        self.mainLayout = QGridLayout()

        self.mainLayout.addWidget(ValueGB('Enabled ', self.actor.models['xcu_r0'], 'ionpump1', 0, '{:g}'), 0, 0)
        self.mainLayout.addWidget(ValueGB('Voltage(V)', self.actor.models['xcu_r0'], 'ionpump1', 1, '{:g}'), 0, 1)
        self.mainLayout.addWidget(ValueGB('Current(A)', self.actor.models['xcu_r0'], 'ionpump1', 2, '{:g}'), 0, 2)
        self.mainLayout.addWidget(ValueGB('Temperature(K)', self.actor.models['xcu_r0'], 'ionpump1', 3, '{:g}'), 0, 3)
        self.mainLayout.addWidget(ValueGB('Pressure(Torr)', self.actor.models['xcu_r0'], 'ionpump1', 4, '{:g}'), 0, 4)

        self.mainLayout.addWidget(ValueGB('Enabled ', self.actor.models['xcu_r0'], 'ionpump2', 0, '{:g}'), 1, 0)
        self.mainLayout.addWidget(ValueGB('Voltage(V)', self.actor.models['xcu_r0'], 'ionpump2', 1, '{:g}'), 1, 1)
        self.mainLayout.addWidget(ValueGB('Current(A)', self.actor.models['xcu_r0'], 'ionpump2', 2, '{:g}'), 1, 2)
        self.mainLayout.addWidget(ValueGB('Temperature(K)', self.actor.models['xcu_r0'], 'ionpump2', 3, '{:g}'), 1, 3)
        self.mainLayout.addWidget(ValueGB('Pressure(Torr)', self.actor.models['xcu_r0'], 'ionpump2', 4, '{:g}'), 1, 4)

        self.mainLayout.addWidget(ValueGB('Cooler_Setpoint(K)', self.actor.models['xcu_r0'], 'coolerTemps', 0, '{:g}'),
                                  2, 0)
        self.mainLayout.addWidget(ValueGB('Cooler_Reject(C)', self.actor.models['xcu_r0'], 'coolerTemps', 1, '{:g}'), 2,
                                  1)
        self.mainLayout.addWidget(ValueGB('Cooler_Tip(K)', self.actor.models['xcu_r0'], 'coolerTemps', 2, '{:g}'), 2, 2)
        self.mainLayout.addWidget(ValueGB('Cooler_Power(W)', self.actor.models['xcu_r0'], 'coolerTemps', 3, '{:g}'), 2,
                                  3)

        self.mainLayout.addWidget(ValueGB('Shutters', self.actor.models['enu'], 'shutters', 2, '{:s}'), 3, 0)

        self.commandLine = QLineEdit()
        self.commandButton = QPushButton('Send Command')
        self.commandButton.clicked.connect(self.sendCommand)

        self.logArea = LogArea()

        self.mainLayout.addWidget(self.commandLine, 4, 0, 1, 4)
        self.mainLayout.addWidget(self.commandButton, 4, 4, 1, 1)
        self.mainLayout.addWidget(self.logArea, 5, 0, 10, 5)
        self.setLayout(self.mainLayout)

    @property
    def actor(self):
        return self.mainTree.actor

    def sendCommand(self):
        [actor, cmdStr] = self.commandLine.text().split(' ', 1)

        self.logArea.newLine('cmdIn=%s %s' % (actor, cmdStr))
        self.actor.cmdr.bgCall(**dict(actor=actor,
                                      cmdStr=cmdStr,
                                      timeLim=600,
                                      callFunc=self.returnFunc))

    def returnFunc(self, cmdVar):
        self.logArea.newLine('cmdOut=%s' % cmdVar.lastReply.canonical())
