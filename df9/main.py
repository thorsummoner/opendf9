#!/usr/bin/env python

import window
import os

class OpenDf9Window(window.Window):
    """
        Main application window
    """

    GLADE_FILE = '.glade'

    def __init__(self, dev=False):
        super(OpenDf9Window, self).__init__()


    class Handler(window.Window.BaseHandler):
        """
            Main Window Event Handler
        """
