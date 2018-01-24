import logging

import actorcore.ICC
from actorcore.QThread import QThread, QMsg
import queue


class OneshotThread(QThread):
    def __init__(self, actor):
        QThread.__init__(self, actor, 'oneshot', timeout=0.2)
        self.returnQueue = []

        self.start()

    def handleTimeout(self):
        if self.returnQueue:
            cmdVar = self.returnQueue[-1].get()
            self.actor.dummyLab.setText('cmdOut=%s' % cmdVar.lastReply.canonical())
            self.exit()
        else:
            pass

    def callFunc(self, method, callTimeout=10.0, urgent=False, **argd):
        """ send ourself a new message.

        Args:
            method: a function or bound method to call
            **argd: the arguments to the method.
        """
        self.returnQueue.append(queue.Queue())
        qmsg = QMsg(method, returnQueue=self.returnQueue[-1], **argd)
        self.queue.put(qmsg, urgent=urgent)


class OurActor(actorcore.ICC.ICC):
    def __init__(self, name, productName=None, modelNames=None, configFile=None, logLevel=logging.INFO):
        # This sets up the connections to/from the hub, the logger, and the twisted reactor.
        #
        modelNames = [] if modelNames is None else modelNames
        actorcore.ICC.ICC.__init__(self, name,
                                   productName=productName,
                                   configFile=configFile,
                                   modelNames=modelNames)

        self.logger.setLevel(logLevel)
        self.everConnected = False

    def connectionMade(self):
        if self.everConnected is False:
            logging.info("alive!!!!")
            self.everConnected = True

    def disconnectActor(self):
        self.shuttingDown = True

    def threadCmd(self, **kwargs):
        # self.cmdr.call(**kwargs)
        cmdrThread = OneshotThread(self)
        cmdrThread.callFunc(self.cmdr.call, **kwargs)

    def updateLog(self, msg):
        print (msg)
        self.logArea.newLine(msg)


def connectActor(modelNames):
    theActor = OurActor('templategui',
                        productName='templateGUI',
                        modelNames=modelNames,
                        logLevel=logging.DEBUG)

    theActor.run(doReactor=False)
    return theActor
