import os
import time
import datetime
import random
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

    text_date_format = "%m/%d/%Y (%a) Daily"
    wait_time = 5

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
        self.text_date = self._date.strftime(DailyAsanaProject.text_date_format)

    def jiggle(self, coordinates):
        '''
        It seems to help to jiggle the mouse sometimes; this isn't just for mouse enter / mouse move, but the events come 
        so fast that I think some software needs to handle the move event before properly handling click... or something.
        Do this randomly because we don't need determinism in a jiggle.
        '''
        x = coordinates[0]
        y = coordinates[1]
        for i in range(10):
            jiggle_x = x + random.randint(-3, 3)
            jiggle_y = y + random.randint(-3, 3)
            pyautogui.moveTo((jiggle_x, jiggle_y))
            time.sleep(0.1)
        pyautogui.moveTo((x, y))

    def instantiate_template(self):
        retina_center = util.find_image("asana_use_template.png")
        self.jiggle(retina_center)
        pyautogui.click()
        util.notify(title="Waiting for {DailyAsanaProject.wait_time} seconds", text="Asana needs to instantiate template", timeout=DailyAsanaProject.wait_time * 1000)
        LOG.info("Creating project for {self.text_date}")
        pyautogui.write(self.text_date)
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
        self.jiggle(retina_center)
        pyautogui.click()

    def add_to_portfolio(self):
        self.new_tab("https://app.asana.com/0/portfolio/1203786245754929/list")
        util.notify(title=f"Waiting for {DailyAsanaProject.wait_time} seconds", text="Loading the portfolio", timeout=DailyAsanaProject.wait_time * 1000)
        retina_center = util.find_image("asana_add_work.png", 0.6)
        self.jiggle(retina_center)
        pyautogui.click()
        pyautogui.write(self.text_date)
        time.sleep(3) #typeahead
        pyautogui.press("enter")
        util.notify(title=f"Waiting for {DailyAsanaProject.wait_time} seconds", text="Waiting for project to show up in the portfolio", timeout=DailyAsanaProject.wait_time * 1000)

    def set_project_color(self):
        # Find the new project by its icon
        retina_center = util.find_image("asana_new_project_icon.png", 0.6)
        self.jiggle(retina_center)
        pyautogui.click()
        time.sleep(1) #Load page; should be quick
        # Find the icon *again*
        retina_center = util.find_image("asana_new_project_icon.png", 0.6)
        self.jiggle(retina_center)
        pyautogui.click()
        # OK, at this point we have the color picker out.
        # Let's choose the right color based on the day.
        # Remember, 0=monday.
        day_of_week = self._date.weekday()
        def click_color(day):
            retina_center = util.find_image(f"asana_{day}_color.png", 0.95)
            self.jiggle(retina_center)
            pyautogui.click()

        if day_of_week == 0:
            click_color("monday")
        elif day_of_week == 1:
            click_color("tuesday")
        elif day_of_week == 2:
            click_color("wednesday")
        elif day_of_week == 3:
            click_color("thursday")
        elif day_of_week == 4:
            click_color("friday")
        elif day_of_week == 5:
            click_color("saturday")
        elif day_of_week == 6:
            click_color("sunday")

    def execute(self):
        util.activate_dock_app_by_image("chrome_in_dock.png")
        self.new_tab("https://app.asana.com/0/project-templates/1203786245754952/list")
        util.notify(title=f"Waiting for {DailyAsanaProject.wait_time} seconds", text="Asana needs to load", timeout=DailyAsanaProject.wait_time * 1000)
        self.instantiate_template()
        # OK, we have a new project! Add it to the portfolio
        self.add_to_portfolio()
        self.set_project_color()
