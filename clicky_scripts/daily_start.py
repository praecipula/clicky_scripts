# A way to get the 'dashboard' of my day:

# Open Asana's MyTasks
# Open Google Calendar
# Open Gmail


import os
import time
import pyautogui
import clicky_scripts.util as util
import logging
import python_logging_base
from python_logging_base import ASSERT

LOG = logging.getLogger("daily_start")
LOG.setLevel(logging.TRACE)

class DailyStart:

    @staticmethod
    def new_tab(address):
        LOG.info(f"Opening tab at {address}")
        with pyautogui.hold('command'):
            pyautogui.press('t')
        time.sleep(0.5)
        pyautogui.write(address)
        pyautogui.press("enter")


    def execute(self):
        util.activate_dock_app_by_image("chrome_in_dock.png")
        pyautogui.rightClick()
        LOG.info(f"Creating a new Chrome window")
        new_window_menu = util.find_image("chrome_new_window.png")
        pyautogui.moveTo(new_window_menu)
        pyautogui.click()
        time.sleep(0.25)
        util.notify("Waiting 1 second", "window needs to load", 1000)
        pyautogui.write("https://news.google.com")
        pyautogui.press("enter")
        self.new_tab("https://calendar.google.com")
        self.new_tab("https://mail.google.com")
        self.new_tab("https://app.asana.com")
