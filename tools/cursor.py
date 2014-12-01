# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5 import QtGui

class AutoCursor(object):
    def __init__(self, widget, shape):
        super(AutoCursor, self).__init__()
        self.widget = widget
        self.shape = shape

    def __enter__(self):
        self.old_cursor = self.widget.cursor()
        self.new_cursor = QtGui.QCursor(self.shape)
        self.widget.setCursor(self.new_cursor)

    def __exit__(self, type, value, traceback):
        self.widget.setCursor(self.old_cursor)
        return type is None

    def setShape(self, shape):
        self.new_cursor.setShape(shape)

    def setArrow(self):
        self.setShape(QtCore.Qt.ArrowCursor)

    def setWait(self):
        self.setShape(QtCore.Qt.WaitCursor)

    def setBusy(self):
        self.setShape(QtCore.Qt.BusyCursor)

class BusyCursor(AutoCursor):
    def __init__(self, widget):
        super(BusyCursor, self).__init__(widget, QtCore.Qt.BusyCursor)

class WaitCursor(AutoCursor):
    def __init__(self, widget):
        super(WaitCursor, self).__init__(widget, QtCore.Qt.WaitCursor)

