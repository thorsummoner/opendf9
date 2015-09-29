#!/usr/bin/env python

"""
    Open DF9 Main
"""

import df9.gui.window
import df9.gui.command

import df9.mission_command

class OpenDf9Window(df9.gui.window.Window):
    """
        Main application window
    """

    GLADE_FILE = 'df9/.glade'
    CSS_PROVIDER_FILE = 'df9/.css'

    main_container = None
    commands = None
    _command = None

    def __init__(self):
        super(OpenDf9Window, self).__init__()
        self.main_container = self.window
        self.commands = dict()

        self.register_command(df9.mission_command.LoadingScreen)
        self.command('LoadingScreen', df9.mission_command.EdenLauncher)

    def register_command(self, command):
        """
            Add a command to the loaded commands list
        """

        self.commands[command.__name__] = command

    def command(self, command_name, post_register=None):
        """
            Replace the current command with command `command_name`
            from the `commands`

            Args:
                command_name: Class name of the command module to display
                post_register: After displaying the command_name module
                    register this new class and display it.
        """

        self.replace_child(self.main_container, self.commands[command_name])
        self._command = command_name

        if post_register is not None:
            self.register_command(post_register)
            self.command(post_register.__class__.__name__)


    #pylint: disable=too-few-public-methods, undefined-variable, no-init
    class Handler(df9.gui.window.Window.Handler):
        """
            Main Window Event Handler
        """
