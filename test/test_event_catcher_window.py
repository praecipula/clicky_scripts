import time
from .event_catcher_window import EventCatcherWindow
import threading


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
    print("Start a thread to do the so-called real work")
    thread = threading.Thread(target=threaded_event_catcher_window_work, args=(window,))
    thread.start()
    print("Sending start. This will block")
    window.start() #blocks
    print("Also join on the worker thread")
    thread.join()
    print("And this should exit.")


def threaded_event_catcher_window_work(window):
    print("Sleep for 2 seconds to allow TK to do its thing.")
    time.sleep(2)
    print("Sending close window event")
    window.incoming_messages.put(EventCatcherWindow.CLOSE_WINDOW)
