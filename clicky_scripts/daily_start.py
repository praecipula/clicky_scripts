# A way to get the 'dashboard' of my day:

# Open Asana's MyTasks
# Open Google Calendar
# Open Gmail


import os
import time
import pyautogui
import logging
import python_logging_base
from python_logging_base import ASSERT

LOG = logging.getLogger("daily_start")
LOG.setLevel(logging.TRACE)

class DailyStart:

    @staticmethod
    def find_image(image):
        image_location = os.path.dirname(__file__) + '/' + image
        LOG.info(f"Finding image {image_location}")
        location = pyautogui.locateOnScreen(image_location, grayscale=True, confidence=0.6)
        if location == None:
            raise Exception(f"Couldn't find chrome icon matching dock icon; reference img {image_location}")
        center = pyautogui.center(location)
        retina_center = [c / 2 for c in center]
        LOG.trace(f"Image found at (non-retina coords) {center}; retina coords {retina_center}")
        return retina_center

    @staticmethod
    def new_tab(address):
        LOG.info(f"Opening tab at {address}")
        with pyautogui.hold('command'):
            pyautogui.press('t')
        time.sleep(0.5)
        pyautogui.write(address)
        pyautogui.press("enter")


    def execute(self):
        screen_size = pyautogui.size()
        retina_center = self.find_image("chrome_in_dock.png")
        ASSERT(retina_center[1] > screen_size[1] - (0.2 * screen_size[1]), "Expected icon to be in dock (last 20% of screen height)")
        pyautogui.moveTo(retina_center)
        pyautogui.rightClick()
        LOG.info(f"Creating a new Chrome window")
        new_window_menu = self.find_image("chrome_new_window.png")
        pyautogui.moveTo(new_window_menu)
        pyautogui.click()
        time.sleep(0.75) # to allow for "new window opening" animation
        pyautogui.write("https://news.google.com")
        pyautogui.press("enter")
        self.new_tab("https://calendar.google.com")
        self.new_tab("https://mail.google.com")
        self.new_tab("https://app.asana.com")
