#!/usr/bin/env python

import sys
import logging 
import time
from queue import Queue
from threading import Thread

from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QLabel
from PyQt6 import QtCore, QtGui

import pyautogui
import python_logging_base
LOG = logging.getLogger("gui_window")
LOG.setLevel(logging.TRACE)

from clicky_scripts import DailyStart
from clicky_scripts import DailyAsanaProject
from clicky_scripts import KeepUpdating


class MainWindow(QMainWindow):
    def __init__(self, * args, **kwargs):
        kwargs['flags'] = QtCore.Qt.WindowType.WindowStaysOnTopHint
        super().__init__(*args, **kwargs)

        self._central_widget = QWidget()
        self.setCentralWidget(self._central_widget)

        self._main_layout = QVBoxLayout()
        self._central_widget.setLayout(self._main_layout)

        self._information_label = QLabel()
        self._information_label.setText("This will display coords")
        self._main_layout.addWidget(self._information_label)

        self._update_timer = QtCore.QTimer()
        self._update_timer.timeout.connect(self.updateData)
        self._update_timer.start(250)

        self._cursor = QtGui.QCursor()


    def updateData(self):
        '''
        '''

        mouse_location = self._cursor.pos()
        # A little too verbose, even for trace.
        # LOG.trace(f"Mouse: {mouse_location.x()}, {mouse_location.y()}")

        # HACK: getting and restoring state instead of just reading the state.
        # keyboard doesn't seem capable of just reading the state.
        x = mouse_location.x()
        y = mouse_location.y()
        # Multiplied because retina screen
        color = pyautogui.pixel(x*2, y*2)
        #LOG.trace(f"Current info on mouse: {mouse_location.x(), mouse_location.y()}")
        updated_info = f"Cursor position: {x}, {y}\n" + \
                f"Color: {color}"
        self._information_label.setText(updated_info)


app = QApplication(sys.argv)



window = MainWindow()
window.show()

app.exec()

