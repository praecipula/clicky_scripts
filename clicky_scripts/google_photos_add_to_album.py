import time
import datetime
import pyautogui
import clicky_scripts.util as util
import logging
import python_logging_base
from python_logging_base import ASSERT

LOG = logging.getLogger("daily_start")
LOG.setLevel(logging.TRACE)

class GooglePhotosAddToAlbum:
    def execute(self):
        start_time = datetime.datetime.now()
        # In google storage manager, right click file name
        LOG.trace("Starting from right click on file in storage manager")
        pyautogui.press('esc')
        LOG.trace("Copy")
        pyautogui.hotkey('command', 'c')
        LOG.trace("Tab 1")
        pyautogui.hotkey('command', '1')
        LOG.trace("Moving to search bar")
        pyautogui.moveTo(600, 160, 0.5)
        pyautogui.click()
        LOG.trace("Pasting into search bar and searching ")
        pyautogui.hotkey('command', 'a')
        pyautogui.hotkey('command', 'v')
        pyautogui.press('enter')
        time.sleep(0.5)
        LOG.trace("Selecting first item")
        pyautogui.moveTo(140, 400, 0.5)
        pyautogui.click()
        time.sleep(0.5)
        LOG.trace("Moving to hamburger menu and clicking")
        # Interestingly, doesn't seem to send mouseMove events to JS when moving, causing
        # the GUI to fade. Click once to wake up before moving.
        pyautogui.click()
        pyautogui.moveTo(1500, 170, 0.5)
        pyautogui.click()
        time.sleep(0.25)
        LOG.trace("Moving to 'Add to album' menu and clicking")
        pyautogui.moveTo(1400, 320, 0.5)
        pyautogui.click()
        time.sleep(2)
        LOG.trace("Moving to top suggested album and clicking")
        pyautogui.moveTo(700, 520, 0.5)
        pyautogui.click()
        time.sleep(1)
        pyautogui.press('esc')
        LOG.trace("Done!")
        end_time = datetime.datetime.now()
        delta = end_time - start_time
        LOG.info(f"Ran in {delta.total_seconds()} seconds")
