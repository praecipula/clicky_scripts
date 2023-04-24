#!/usr/bin/env python

import sys
import logging 
import time
import io
from queue import Queue
from threading import Thread, Lock

import cProfile, pstats

from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QLabel, QSlider, QGraphicsScene, QGraphicsView, QGraphicsLineItem
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor, QTransform, QColor, QPixmap, QGuiApplication
import PIL
from PIL.ImageQt import ImageQt

import pyautogui
import subprocess
import python_logging_base

LOG = logging.getLogger("gui_window")
LOG.setLevel(logging.TRACE)
# Pillow is a little noisy by default, so let's up that one logger.
logging.getLogger("PIL.PngImagePlugin").setLevel(logging.INFO)

class UpdateScreenshotThread(Thread):
    def __init__(self, *args, **kwargs):
        self._lock = Lock()
        self._screenshot = None
        super().__init__(*args, **kwargs)
        self.daemon = True

    def get_screenshot(self):
        with self._lock:
            return self._screenshot

    def run(self):
        pauseRate = 0.25 #seconds of sleep time between updates so we're not just
        # constantly taking screenshots.
        while True:

            try:
                # pyautogui and pyscreeze do some other stuff that makes things slower and
                # scattered screenshots in the filesystem; calling `screencapture` is
                # effectively what they're doing under the hood anyway, so let's do that.

                # For the sake of not constantly writing to disk, doing this to ramdisk
                # is a nice feature.
                LOG.todo("Add the capability to dynamically mount a ram disk")
                screenshot_filename = '/Volumes/screenshot_ramdisk/tmp_screenshot.png'
                #-x - no sounds
                #-R (x,y,w,h) region
                result = subprocess.run(['screencapture',
                                         '-x',
                                         screenshot_filename],
                                         capture_output=True)
                if result.returncode != 0:
                    import pdb; pdb.set_trace()
                    raise Exception("Screencapture run failed")
                screenshot = PIL.Image.open(screenshot_filename)
            except IndexError as e:
                LOG.warning("Index error: {region} out of range. Recall that the app must run on the primary screen AND the primary screen needs to be the laptop screen.")
                LOG.todo("In the future we can probably find a better way to take screenshots that would include the correct screen (this is another example of pyautogui and its screenshot disagreeing about image coordinates, as the secondary screen messes up screenshots based on the primary screen's coordinates)")
                time.sleep(pauseRate)
                continue

            # Set shared variables
            with self._lock:
                self._screenshot = screenshot
            time.sleep(pauseRate)


class MainWindow(QMainWindow):
    def __init__(self, * args, **kwargs):
        kwargs['flags'] = Qt.WindowType.WindowStaysOnTopHint
        super().__init__(*args, **kwargs)

        # Timer-based insetead of event-based events. Timer based because they just might occur
        # when this window is not directly receiving focus (so we poll for e.g. mouse position to
        # update in the bg.
        self._update_position_timer = QTimer()
        self._update_position_timer.timeout.connect(self.updatePositionData)
        self._update_position_timer.start(50)
        self._update_pixel_timer = QTimer()
        self._update_pixel_timer.timeout.connect(self.updatePixelData)
        self._update_pixel_timer.start(50)
        self._update_screenshot_thread = UpdateScreenshotThread()
        self._update_screenshot_thread.start()

        # For when we want multi-screen support self._screens = QGuiApplication.screens()
        self._screen_dimensions = QGuiApplication.primaryScreen().geometry()

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
        self._neighborhood_slider.setValue(50)
        self._main_layout.addWidget(self._neighborhood_slider)

        self._cursor = QCursor()
        self._mouse_color=(0, 0, 0)

        self._graphics_scene = QGraphicsScene(parent=self)
        self._color_rectangle = self._graphics_scene.addRect(0, 0, 100, 100)
        self._neighborhood_rectangle = self._graphics_scene.addRect(0, 0, 100, 100)
        self._n_r_reticle_vertical = QGraphicsLineItem(50, 0, 50, 100, self._neighborhood_rectangle)
        self._n_r_reticle_horizontal= QGraphicsLineItem(0, 50, 100, 50, self._neighborhood_rectangle)
        neighborhood_rectangle_transform = QTransform().translate(0, 100)
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
        screenshot = self._update_screenshot_thread.get_screenshot()
        if screenshot != None:
            try:
                # Retina screen to full-pixel screenshot
                retina_pixel_coords = (min(mouse_location.x() * 2, self._screen_dimensions.width() - 1), 
                                       min(mouse_location.y() * 2, self._screen_dimensions.height() - 1))
                pix = screenshot.getpixel(retina_pixel_coords)
            except IndexError as e:
                import pdb; pdb.set_trace()
                LOG.warning(f"Attempt to get out-of-range pixel {retina_pixel_coords} from screenshot");
            self._mouse_color = (pix[0], pix[1], pix[2])
        else:
            self._mouse_color = None
        updated_info = f"Cursor position: {mouse_location.x()}, {mouse_location.y()}\n" + \
                f"Color: {self._mouse_color}"
        self._information_label.setText(updated_info)

    def updatePixelData(self):
        if hasattr(self, "_cursor"):
            mouse_location = self._cursor.pos()
            screenshot = self._update_screenshot_thread.get_screenshot()
            
            neighborhood_size = self._neighborhood_slider.value()
            half_neighborhood_size = neighborhood_size / 2


            if self._mouse_color != None:
                color = QColor(self._mouse_color[0], self._mouse_color[1], self._mouse_color[2])
                brush = self._color_rectangle.brush()
                brush.setColor(color)
                brush.setStyle(Qt.BrushStyle.SolidPattern)
                self._color_rectangle.setBrush(brush)

            if screenshot != None:
                brush = self._neighborhood_rectangle.brush()
                # Scale the image to rectangle height, and the rectangle width to scaled image width.
                # That is, vertical zoom, horizontal stretch.
                rectangle_dimensions = self._neighborhood_rectangle.rect()
                # I got a warning for using this - apparently according to the
                # source, setTexture further down is the way to go, no need
                # to set TexturePattern as the style.
                # brush.setStyle(Qt.BrushStyle.TexturePattern)

                subimage = screenshot.crop((mouse_location.x()*2 - half_neighborhood_size,
                                           mouse_location.y()*2 - half_neighborhood_size,
                                           mouse_location.x()*2 + half_neighborhood_size,
                                           mouse_location.y()*2 + half_neighborhood_size))
                qim = ImageQt(subimage)
                pix = QPixmap.fromImage(qim).scaledToHeight(int(rectangle_dimensions.height()))
                brush.setTexture(pix)
                self._neighborhood_rectangle.setBrush(brush)
                # Now to draw reticle of inverse of central pixel's color
                inverse_color = QColor(255 - color.red(), 255 - color.green(), 255 - color.blue())
                r_v_pen = self._n_r_reticle_vertical.pen()
                r_v_pen.setWidth(1)
                r_v_pen.setColor(inverse_color)
                self._n_r_reticle_vertical.setPen(r_v_pen)
                r_h_pen = self._n_r_reticle_horizontal.pen()
                r_h_pen.setWidth(1)
                r_h_pen.setColor(inverse_color)
                self._n_r_reticle_horizontal.setPen(r_h_pen)

    def keyPressEvent(self, keyEvent):
        # Just to highlight how these keys are remapped on OS X - note "control" is strange!
        ctrl = Qt.KeyboardModifier.MetaModifier
        opt = Qt.KeyboardModifier.AltModifier
        cmd = Qt.KeyboardModifier.ControlModifier

        # Plain key events - not using modifiers.
        LOG.todo("Will we ever need to capture plain keystrokes for arrows or +/-? Maybe...")
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

        elif (keyEvent.modifiers() == ctrl | opt | cmd):
            if (keyEvent.key() == Qt.Key.Key_Space):
                LOG.info("Would capture")




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

