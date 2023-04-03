#!/usr/bin/env python

import sys
import logging 
import time
import io
from queue import Queue
from threading import Thread

import cProfile, pstats

from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QLabel, QGraphicsScene, QGraphicsView
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

        self._graphics_scene = QGraphicsScene(parent=self)
        self._color_rectangle = self._graphics_scene.addRect(0, 0, 100, 100)
        self._graphics_view = QGraphicsView(self._graphics_scene)
        self._graphics_view.show()
        self._main_layout.addWidget(self._graphics_view)


        self._cursor = QtGui.QCursor()
        self._mouse_color=(0, 0, 0)
        self._update_position_timer = QtCore.QTimer()
        self._update_position_timer.timeout.connect(self.updatePositionData)
        self._update_position_timer.start(10)
        self._update_pixel_timer = QtCore.QTimer()
        self._update_pixel_timer.timeout.connect(self.updatePixelData)
        self._update_pixel_timer.start(1000)


    def updatePositionData(self):
        '''
        '''
        
        mouse_location = self._cursor.pos()
        # A little too verbose, even for trace.
        #LOG.trace(f"Current info on mouse: {mouse_location.x(), mouse_location.y()}")
        updated_info = f"Cursor position: {mouse_location.x()}, {mouse_location.y()}\n" + \
                f"Color: {self._mouse_color}"
        self._information_label.setText(updated_info)

    def updatePixelData(self):
        if hasattr(self, "_cursor"):
            mouse_location = self._cursor.pos()
            self._mouse_color = pyautogui.pixel(mouse_location.x()*2 - 1, mouse_location.y()*2 - 1)
            color = QtGui.QColor(self._mouse_color[0], self._mouse_color[1], self._mouse_color[2])
            brush = self._color_rectangle.brush()
            brush.setColor(color)
            brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
            self._color_rectangle.setBrush(brush)
            LOG.info(color.red())
            self._graphics_scene.update()



app = QApplication(sys.argv)



window = MainWindow()
window.show()

pr = cProfile.Profile()
pr.enable()
app.exec()
pr.disable()

s = io.StringIO()
sortby = pstats.SortKey.CUMULATIVE
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue())

