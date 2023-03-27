import logging
import python_logging_base

LOG = logging.getLogger("clicky")
LOG.setLevel(logging.TRACE)

from clicky_scripts.cliclick_base import CliClick
from clicky_scripts.get_mouse_coordinates import GetMouseCoordinates
from clicky_scripts.click import Click
from clicky_scripts.right_click import RightClick
