import os
import time
import datetime
import pyautogui
import clicky_scripts.util as util
import logging
import python_logging_base
from python_logging_base import ASSERT

LOG = logging.getLogger("daily_start")
LOG.setLevel(logging.TRACE)

class DailyAsanaProject:
    '''
    Clone and create a new project of the day in Asana.
    '''

    @staticmethod
    def new_tab(address):
        LOG.info(f"Opening tab at {address}")
        with pyautogui.hold('command'):
            pyautogui.press('t')
        time.sleep(0.25)
        pyautogui.write(address)
        pyautogui.press("enter")

    def __init__(self, date = datetime.datetime.today()):
        self._date = date

    def execute(self):
        util.activate_dock_app_by_image("chrome_in_dock.png")
        self.new_tab("https://app.asana.com/0/project-templates/1203786245754952/list")
        util.notify(title="Waiting for 3 seconds", text="Asana needs to load", timeout=3000)
        retina_center = util.find_image("asana_use_template.png")
        pyautogui.moveTo(retina_center)
        pyautogui.click()
        util.notify(title="Waiting for 3 seconds", text="Asana needs to instantiate template", timeout=3000)
        text_date_format = self._date.strftime("%m/%d/%Y (%a) Daily")
        LOG.info("Creating project for {text_date_format}")
        pyautogui.write(text_date_format)
        # Tab 3 times to get to the date picker
        for i in range(3):
            pyautogui.press("tab")
        # Backspace a bunch
        for i in range(10):
            pyautogui.press("backspace")
        date_picker_date_format = self._date.strftime("%m/%d/%Y")
        pyautogui.write(date_picker_date_format)
        pyautogui.press("enter")
        retina_center = util.find_image("asana_create_project.png")
        pyautogui.moveTo(retina_center)
        pyautogui.click()
        # OK, we have a new project! Add it to the portfolio
        self.new_tab("https://app.asana.com/0/portfolio/1203786245754929/list")
        util.notify(title="Waiting for 3 seconds", text="Loading the portfolio", timeout=3000)
        retina_center = util.find_image("asana_add_work.png", 0.6)
        pyautogui.moveTo(retina_center)
        pyautogui.click()
        pyautogui.write(text_date_format)
        time.sleep(3) #typeahead
        pyautogui.press("enter")
