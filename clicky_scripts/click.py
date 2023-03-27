import logging
import python_logging_base

LOG = logging.getLogger("clicky")
LOG.setLevel(logging.TRACE)

from clicky_scripts.cliclick_base import CommandBase

class Click(CommandBase):
    '''
    Clicking can be done without moving the mouse to the given coordinates;
    however, it's sometimes good to consider that moving the mouse is a good
    feedback cue for the user, so unless speed is paramount, I'd recommend
    doing a move to and then click at.
    '''

    def __init__(self, x, y):
        super().__init__(f"c:{x},{y}")
        self._x = x
        self._y = y

    def expects_output(self):
        return False

    def __repr__(self):
        return f"<Click: x={self._x}, y={self._y}>"
