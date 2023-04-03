#!/usr/bin/env python

import sys
import logging 
import time
import io
from queue import Queue
from threading import Thread, Lock

import cProfile, pstats

from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QLabel, QGraphicsScene, QGraphicsView
from PyQt6 import QtCore, QtGui
from PIL.ImageQt import ImageQt

import pyautogui
import python_logging_base
LOG = logging.getLogger("gui_window")
LOG.setLevel(logging.TRACE)

from clicky_scripts import DailyStart
from clicky_scripts import DailyAsanaProject
from clicky_scripts import KeepUpdating


class UpdatePixelThread(Thread):
    def __init__(self, *args, **kwargs):
        self._lock = Lock()
        self._mouse_location = None
        self._color = None
        self._neighborhood = None
        super().__init__(*args, **kwargs)
        self.daemon = True

    def set_mouse_location(self, location):
        with self._lock:
            self._mouse_location = location

    def get_color(self):
        with self._lock:
            return self._color
    
    def get_neighborhood(self):
        with self._lock:
            return self._neighborhood

    def run(self):
        updateRate = 0.25 #seconds of sleep time between updates
        while True:
            mouse_location = None
            # Get shared variable
            with self._lock:
                mouse_location = self._mouse_location
            if mouse_location == None: # Hasn't been set by GUI yet.
                time.sleep(updateRate)
                continue

            # This takes some time, so be unlocked with local variables until setting at the end.
            mouse_color = self._mouse_color = pyautogui.pixel(mouse_location.x()*2 - 1, mouse_location.y()*2 - 1)
            half_neighborhood = 50 #This is retina / screen pixels, not raw / screenshot pixels
            # OK, still need to work some math here.
            region = (mouse_location.x()*2 - half_neighborhood, mouse_location.y()*2 - half_neighborhood,
                      half_neighborhood * 2, half_neighborhood * 2)
            mouse_neighborhood = pyautogui.screenshot(region=region)
            mouse_neighborhood.save("/tmp/screen.png")

            # Set shared variables
            with self._lock:
                self._color = mouse_color
                self._neighborhood = mouse_neighborhood
            time.sleep(updateRate)


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
        self._neighborhood_rectangle = self._graphics_scene.addRect(0, 100, 100, 100)
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
        self._update_pixel_timer.start(10)
        self._update_pixel_thread = UpdatePixelThread()
        self._update_pixel_thread.start()


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
            self._update_pixel_thread.set_mouse_location(mouse_location)
            color = self._update_pixel_thread.get_color()
            neighborhood = self._update_pixel_thread.get_neighborhood()
            
            if color != None:
                color = QtGui.QColor(color[0], color[1], color[2])
                brush = self._color_rectangle.brush()
                brush.setColor(color)
                brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
                self._color_rectangle.setBrush(brush)

            if neighborhood != None:
                brush = self._neighborhood_rectangle.brush()
                brush.setStyle(QtCore.Qt.BrushStyle.TexturePattern)
                qim = ImageQt(neighborhood)
                pix = QtGui.QPixmap.fromImage(qim)
                brush.setTexture(pix)
                self._neighborhood_rectangle.setBrush(brush)





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

