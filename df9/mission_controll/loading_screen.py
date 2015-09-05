"""
    Loading screen

    TODO:
     - [ ] Loading Preroll
        - [ ] Skip indicator obvious when loading complete
        - [ ] Display short slides if user has skipped before
        - [ ] Credit:
            - [ ] Doubble Fine (Inspiration, Core)
            - [ ] Chris Sawyer (RTC 1,2, TTD) (Inspiration)
            - [ ] FOSS Software (Topic)
            - [ ] Python (Topic)
            - [ ] Branding for Open source games (Topic)
            - [ ] System76 for Hardware (Special Thanks)
"""

import textwrap

import df9.version_git
from df9.mission_controll import MissionControll

class LoadingScreen(MissionControll):
    CONTAINER = 'loading'
    def __init__(self, app):
        super(LoadingScreen, self).__init__(app)

        self.loading_ver = app.builder.get_object('loading_ver')

        self.loading_ver.set_text(
            self._version_diguest()
        )

    def _version_diguest(self):
        return textwrap.dedent("""
            Build: {version}
        """).lstrip().format(
            version=df9.version_git.version,
        )
