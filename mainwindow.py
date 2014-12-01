# -*- coding: utf-8 -*-

import json

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from models import JsonTreeModel
from tools.cursor import BusyCursor

from ui_mainwindow import Ui_MainWindow

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # UI initialize
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.initModels()

    def initModels(self):
        self.jsonModel = JsonTreeModel(self)
        self.ui.treeView.setModel(self.jsonModel)

    @QtCore.pyqtSlot()
    def on_actionOpen_triggered(self):
        filepath, ext_filter = QtWidgets.QFileDialog.getOpenFileName(self,
            '',
            '.',
            self.tr('Json (*.json)')
        )
        if not filepath:
            return
        with BusyCursor(self):
            data = json.load(open(str(filepath)))
            self.jsonModel.setJsonDocument(data)

