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
        big_frame = ttk.Frame(self._tk)
        big_frame.pack(fill='both', expand=True)

        label = ttk.Label(big_frame, text='Lorem ipsum')
        label.pack()

        self._tk.geometry('200x200')
        self._tk.after(200, self.process_incoming_messages)
        self._tk.mainloop()

    def process_incoming_messages(self):
        while self._incoming_queue.qsize() > 0:
            message = self._incoming_queue.get()
            if message == EventCatcherWindow.CLOSE_WINDOW:
                self._tk.quit()        
        self._tk.after(100, self.process_incoming_messages)

