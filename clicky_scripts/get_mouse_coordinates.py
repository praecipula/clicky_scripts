import logging
import python_logging_base

LOG = logging.getLogger("clicky")
LOG.setLevel(logging.TRACE)

from clicky_scripts.cliclick_base import CommandBase

class GetMouseCoordinates(CommandBase):

    def __init__(self):
        super().__init__("p:.")
        self._x = None
        self._y = None

    def expects_output(self):
        return True

    def handle_output(self, output_string):
        coords = output_string.split(",")
        self._x = coords[0].strip()
        self._y = coords[1].strip()

    def __repr__(self):
        return f"<GetMouseCoordinates: x={self._x}, y={self._y}>"
