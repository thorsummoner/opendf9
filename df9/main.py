#!/usr/bin/env python

import window
import os

import df9.mission_controll

class OpenDf9Window(window.Window):
    """
        Main application window
    """

    GLADE_FILE = 'df9/.glade'
    CSS_PROVIDER_FILE = 'df9/.css'

    def __init__(self, dev=False):
        super(OpenDf9Window, self).__init__()

        self.main_container = self.window
        if dev:
            # Add an additional frame arround the main display with dev tools
            self.replace_child(self.window, self.builder.get_object('dev'))
            self.main_container = self.builder.get_object('dev-mount')

        # Show loading screen
        self.replace_child(
            self.main_container,
            df9.mission_controll.LoadingScreen(self).widget
        )

        # Show new game screen
        self.replace_child(
            self.main_container,
            df9.mission_controll.EdenLauncher(self).widget
        )

    class Handler(window.Window.BaseHandler):
        """
            Main Window Event Handler
        """
