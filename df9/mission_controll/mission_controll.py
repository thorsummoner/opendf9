
class MissionControll(object):
    CONTAINER = NotImplementedError

    def __init__(self, app):
        super(MissionControll, self).__init__()
        self.app = app
        self.widget = app.builder.get_object(self.CONTAINER)
