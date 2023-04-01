# This is imported into the module-level namespace, so we can put a bunch of util
# functions in this module for all other modules/classes

import os
import time
import logging
import python_logging_base
from python_logging_base import ASSERT
import pyautogui

LOG = logging.getLogger("clicky.util")
LOG.setLevel(logging.TRACE)

def find_image(image, confidence=0.6, **kwargs):
    image_location = os.path.dirname(__file__) + '/image_targets/' + image
    LOG.info(f"Finding image {image_location}")
    location = pyautogui.locateOnScreen(image_location, grayscale=False, confidence=confidence, **kwargs)
    if location == None:
        raise Exception(f"Couldn't find image; reference img {image_location}")
    center = pyautogui.center(location)
    retina_center = [c / 2 for c in center]
    LOG.trace(f"Image found at (non-retina coords) {center}; retina coords {retina_center}")
    return retina_center

def last_active_app(previous=1):
    with pyautogui.hold("command"):
        for i in range(previous):
            pyautogui.press('tab')

def center_mouse():
    '''
    Center the mouse on the screen; that's as good a place as any to not hover.
    It might be useful to do some other functions like this because center might not
    always always be the safe place.
    '''
    screen_size = pyautogui.size()
    pyautogui.moveTo(screen_size[0]/2, screen_size[1]/2)
    time.sleep(0.5)

def activate_dock_app_by_image(image):
    center_mouse()
    screen_size = pyautogui.size()
    max_y = int(screen_size.height - (0.2 * screen_size.height)) # bottom 20 percent of the screen
    non_retina_region = (0, max_y*2, screen_size.width * 2, (screen_size.height - max_y)*2)
    retina_center = find_image(image, region=non_retina_region)
    pyautogui.moveTo(retina_center)
    pyautogui.click()

def notify(title="Waiting for a time", text="Some generic message", timeout=1000):
    pyautogui.confirm(title=title, text=text, timeout=timeout)
    last_active_app()
