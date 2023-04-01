import logging
import python_logging_base

LOG = logging.getLogger("clicky")
LOG.setLevel(logging.TRACE)
# Also, PIL is a bit noisy; up its level.
pil_log = logging.getLogger("PIL.PngImagePlugin")
pil_log.setLevel(logging.INFO)

from clicky_scripts.daily_start import DailyStart
