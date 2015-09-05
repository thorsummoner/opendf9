"""
    Eden initial probe destination picker.
"""

from df9.mission_controll import MissionControll

class EdenLauncher(MissionControll):
    CONTAINER = 'eden'

    def __init__(self, app):
        super(EdenLauncher, self).__init__(app)

