"""
    Base mission command panel
"""

from df9.gui.command import Command

class MissionCommand(Command):
    """
        Replacible Command Screen
    """

    PREFIX = ''

    def __init__(self, app):
        super(MissionControll, self).__init__()
        self.app = app
