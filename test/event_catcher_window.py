import tkinter
from tkinter import ttk
import threading
import queue

import logging
import python_logging_base

LOG = logging.getLogger("test_window")
LOG.setLevel(logging.TRACE)

class EventCatcherWindow:
    '''
    A basic window that can catch events from the test runs. This is how we'll identify that clicks / right clicks / drags etc..
    actually are sent to the window.
    '''

    CLOSE_WINDOW="close"
    

    def __init__(self):
        self._incoming_queue = queue.Queue()
        self._outgoing_queue = queue.Queue()
        self._tk = tkinter.Tk()

    @property
    def outgoing_messages(self):
        return self._outgoing_queue

    @property
    def incoming_messages(self):
        return self._incoming_queue

    def start(self):
        frame = ttk.Frame(self._tk)
        frame.pack(fill='both', expand=True)
        # Set up handlers
        # Left click
        frame.bind("<Button-1>", self.catch_event)
        # Double click
        frame.bind("<Double-Button-1>", self.catch_event)
        # Middle click
        frame.bind("<Button-2>", self.catch_event)
        # Right click
        frame.bind("<Button-3>", self.catch_event)
        # Add more events by following this site:
        # https://python-course.eu/tkinter/events-and-binds-in-tkinter.php
        

        # Some helpful text for info
        label = ttk.Label(frame, text='This frame will catch\nkeyboard and mouse events')
        label.pack()

        self._tk.geometry('200x200')
        self._tk.after(200, self.process_incoming_messages)
        self._tk.mainloop()

    def catch_event(self, event):
        # Handle the event by pushing an event to the outgoing queue
        LOG.debug(event)
        self._outgoing_queue.put(event)


    def process_incoming_messages(self):
        while self._incoming_queue.qsize() > 0:
            message = self._incoming_queue.get()
            if message == EventCatcherWindow.CLOSE_WINDOW:
                self._tk.quit()        
        self._tk.after(100, self.process_incoming_messages)

