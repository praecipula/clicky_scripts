#!/usr/bin/env python

import sys
import logging 
import time
import io
from queue import Queue
from threading import Thread, Lock

import cProfile, pstats

from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QLabel, QSlider, QGraphicsScene, QGraphicsView, QGraphicsLineItem
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt
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
        self._neighborhood_size = 100
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

    def set_neighborhood_size(self, size):
        with self._lock:
            self._neighborhood_size = size

    def run(self):
        pauseRate = 0.25 #seconds of sleep time between updates so we're not just
        # constantly taking screenshots.
        while True:
            mouse_location = None
            # Get shared variable
            with self._lock:
                mouse_location = self._mouse_location
            if mouse_location == None: # Hasn't been set by GUI yet.
                time.sleep(pauseRate)
                continue

            # This takes some time, so be unlocked with local variables until setting at the end.
            mouse_color = self._mouse_color = pyautogui.pixel(mouse_location.x()*2 - 1, mouse_location.y()*2 - 1)
            # OK, still need to work some math here.
            half_neighborhood_size = self._neighborhood_size / 2
            region = (mouse_location.x()*2 - half_neighborhood_size, 
                      mouse_location.y()*2 - half_neighborhood_size,
                      self._neighborhood_size,
                      self._neighborhood_size)
            try:
                mouse_neighborhood = pyautogui.screenshot(region=region)
            except IndexError as e:
                LOG.warning("Index error: {region} out of range. Recall that the app must run on the primary screen AND the primary screen needs to be the laptop screen.")
                LOG.todo("In the future we can probably find a better way to take screenshots that would include the correct screen (this is another example of pyautogui and its screenshot disagreeing about image coordinates, as the secondary screen messes up screenshots based on the primary screen's coordinates)")
                time.sleep(pauseRate)
                continue
            # Useful for debugging
            # mouse_neighborhood.save("/tmp/screen.png")

            # Set shared variables
            with self._lock:
                self._color = mouse_color
                self._neighborhood = mouse_neighborhood
            time.sleep(pauseRate)


class MainWindow(QMainWindow):
    def __init__(self, * args, **kwargs):
        kwargs['flags'] = Qt.WindowType.WindowStaysOnTopHint
        super().__init__(*args, **kwargs)

        # Timer-based insetead of event-based events. Timer based because they just might occur
        # when this window is not directly receiving focus (so we poll for e.g. mouse position to
        # update in the bg.
        self._update_position_timer = QtCore.QTimer()
        self._update_position_timer.timeout.connect(self.updatePositionData)
        self._update_position_timer.start(10)
        self._update_pixel_timer = QtCore.QTimer()
        self._update_pixel_timer.timeout.connect(self.updatePixelData)
        self._update_pixel_timer.start(10)
        self._update_pixel_thread = UpdatePixelThread()
        self._update_pixel_thread.start()

        self._central_widget = QWidget()
        self.setCentralWidget(self._central_widget)

        self._main_layout = QVBoxLayout()
        self._central_widget.setLayout(self._main_layout)

        self._information_label = QLabel()
        self._information_label.setText("This will display coords")
        self._main_layout.addWidget(self._information_label)

        self._neighborhood_slider = QSlider(Qt.Orientation.Horizontal)
        self._neighborhood_slider.setMinimum(4)
        self._neighborhood_slider.setMaximum(100)
        self._neighborhood_slider.setSingleStep(10) # because we are in the even middle of a square
        self._neighborhood_slider.setTickInterval(10)
        self._neighborhood_slider.sliderMoved.connect(self.updateNeighborhoodSize)
        self._neighborhood_slider.valueChanged.connect(self.updateNeighborhoodSize)
        self._neighborhood_slider.setValue(50)
        self._main_layout.addWidget(self._neighborhood_slider)

        self._cursor = QtGui.QCursor()
        self._mouse_color=(0, 0, 0)

        self._graphics_scene = QGraphicsScene(parent=self)
        self._color_rectangle = self._graphics_scene.addRect(0, 0, 100, 100)
        self._neighborhood_rectangle = self._graphics_scene.addRect(0, 0, 100, 100)
        self._n_r_reticle_vertical = QGraphicsLineItem(50, 0, 50, 100, self._neighborhood_rectangle)
        self._n_r_reticle_horizontal= QGraphicsLineItem(0, 50, 100, 50, self._neighborhood_rectangle)
        neighborhood_rectangle_transform = QtGui.QTransform().translate(0, 100)
        self._neighborhood_rectangle.setTransform(neighborhood_rectangle_transform)
        self._graphics_view = QGraphicsView(self._graphics_scene)
        self._graphics_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._graphics_view.show()
        self._main_layout.addWidget(self._graphics_view)



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
                self._mouse_color = color
                color = QtGui.QColor(color[0], color[1], color[2])
                brush = self._color_rectangle.brush()
                brush.setColor(color)
                brush.setStyle(Qt.BrushStyle.SolidPattern)
                self._color_rectangle.setBrush(brush)

            if neighborhood != None:
                brush = self._neighborhood_rectangle.brush()
                # Scale the image to rectangle height, and the rectangle width to scaled image width.
                # That is, vertical zoom, horizontal stretch.
                rectangle_dimensions = self._neighborhood_rectangle.rect()
                # I got a warning for using this - apparently according to the
                # source, setTexture further down is the way to go, no need
                # to set TexturePattern as the style.
                #brush.setStyle(Qt.BrushStyle.TexturePattern)
                qim = ImageQt(neighborhood)
                pix = QtGui.QPixmap.fromImage(qim).scaledToHeight(int(rectangle_dimensions.height()))
                brush.setTexture(pix)
                self._neighborhood_rectangle.setBrush(brush)
                # Now to draw reticle of inverse of central pixel's color
                inverse_color = QtGui.QColor(255 - color.red(), 255 - color.green(), 255 - color.blue())
                r_v_pen = self._n_r_reticle_vertical.pen()
                r_v_pen.setWidth(1)
                r_v_pen.setColor(inverse_color)
                self._n_r_reticle_vertical.setPen(r_v_pen)
                r_h_pen = self._n_r_reticle_horizontal.pen()
                r_h_pen.setWidth(1)
                r_h_pen.setColor(inverse_color)
                self._n_r_reticle_horizontal.setPen(r_h_pen)

    def updateNeighborhoodSize(self):
        LOG.trace(self._neighborhood_slider.value())
        self._update_pixel_thread.set_neighborhood_size(self._neighborhood_slider.value())

    def keyPressEvent(self, keyEvent):
        LOG.trace(keyEvent.text())
        # Why flipped sign? Because '-' feels like "zoom out" which means "smaller neighborhood", and vice versa.
        if (keyEvent.key() == Qt.Key.Key_Minus):
            self._neighborhood_slider.setValue(self._neighborhood_slider.value() + 1)
        elif (keyEvent.key() == Qt.Key.Key_Plus):
            self._neighborhood_slider.setValue(self._neighborhood_slider.value() - 1)
        elif (keyEvent.key() == Qt.Key.Key_Up):
            mouse_location = self._cursor.pos()
            pyautogui.moveTo(mouse_location.x(), mouse_location.y() - 1)
        elif (keyEvent.key() == Qt.Key.Key_Down):
            mouse_location = self._cursor.pos()
            pyautogui.moveTo(mouse_location.x(), mouse_location.y() + 1)
        elif (keyEvent.key() == Qt.Key.Key_Left):
            mouse_location = self._cursor.pos()
            pyautogui.moveTo(mouse_location.x() - 1, mouse_location.y())
        elif (keyEvent.key() == Qt.Key.Key_Right):
            mouse_location = self._cursor.pos()
            pyautogui.moveTo(mouse_location.x() + 1, mouse_location.y())
        




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

