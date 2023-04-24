import logging
import python_logging_base
import pyautogui

LOG = logging.getLogger("clicky")
LOG.setLevel(logging.TRACE)
# Also, PIL is a bit noisy; up its level.
pil_log = logging.getLogger("PIL.PngImagePlugin")
pil_log.setLevel(logging.INFO)

from clicky_scripts.util import *
from clicky_scripts.daily_start import DailyStart
from clicky_scripts.daily_asana_project import DailyAsanaProject
from clicky_scripts.keep_updating import KeepUpdating
from clicky_scripts.google_photos_add_to_album import GooglePhotosAddToAlbum
