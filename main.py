#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from PyQt5 import QtWidgets

from mainwindow import MainWindow

def main():
    app = QtWidgets.QApplication(sys.argv)

    win = MainWindow()
    win.show()

    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())
