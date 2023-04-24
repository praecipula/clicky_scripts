import pyautogui
import clicky_scripts.util as util
import logging
import python_logging_base
from python_logging_base import ASSERT


class KeepUpdating:

    def execute(self):
        while(True):
            util.notify("Mouse is at", f"Position: {pyautogui.position()}", 100)
