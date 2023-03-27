import time
import threading

from .event_catcher_window import EventCatcherWindow
from clicky_scripts import CliClick, Click
from tkinter import EventType

import logging
import python_logging_base

LOG = logging.getLogger("event_catcher_window")
LOG.setLevel(logging.TRACE)

# pytest swallows output
# If you want to see the output, run it with -rP switches.


def test_event_catcher_window():
    '''
    The event catcher window must run in the main thread, which is annoying - all GUI toolkits seem
    to have this restriction.

    This means we need to run _our_ logic in a separate thread to avoid the blocking that the GUI's 
    event loop will initiate.

    So we'll kick off a thread, do the work, and send an event to close the window, when we can join
    and evaluate the results.
    '''
    window = EventCatcherWindow()
    LOG.info("Starting a thread to do the real work")
    thread = threading.Thread(target=threaded_event_catcher_window_work, args=(window,))
    thread.start()
    LOG.debug("Sending start. This will block")
    window.start() #blocks
    LOG.debug("Join on the worker thread; this will block here until after the window closes (by sleeping)")
    thread.join()


def threaded_event_catcher_window_work(window):
    try: 
        initial_sleep = 1
        LOG.debug(f"Sleeping for {initial_sleep} seconds to allow TK to do its thing.")
        time.sleep(initial_sleep)
        LOG.info("Clicking with the mouse")
        clicky = CliClick()
        x_location = 150
        y_location = 150
        c = Click(150, 150)
        clicky.add_command(c)
        clicky.execute()
        LOG.debug("Clicked")
        LOG.info("Sleeping to let the window process")
        time.sleep(1)
        LOG.trace("Dumping the queue, looking for click")
        click_found = False
        while window.outgoing_messages.qsize() > 0:
            event = window.outgoing_messages.get()
            # for the purposes of testing, we don't really care all that much to make the interface friendlier.
            # These are the straight Tk events.
            # Also note that __repr__ gives local, not global screen coordinates. We should check explicitly.
            # Button event, and state is left click / button 1 (integer vals are defined from tkinter)
            # Definition here: https://github.com/python/cpython/blob/3.11/Lib/tkinter/__init__.py
            if (event.type == EventType.ButtonPress and event.num == 1):
                LOG.trace(f"Mouse press event at global loc {event.x_root}, {event.y_root}")
                if (event.x_root == x_location and event.y_root == y_location):
                    LOG.trace("Found expected event.")
                    click_found = True
        assert click_found == True
    finally:
        LOG.info("Sending close event to window")
        window.incoming_messages.put(EventCatcherWindow.CLOSE_WINDOW)
