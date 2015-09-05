
class MissionControll(object):
    CONTAINER = NotImplementedError

    def __init__(self, app):
        super(MissionControll, self).__init__()
        self.app = app
        self.widget = app.builder.get_object(self.CONTAINER)

        if not self.widget:
            raise TypeError('Could not locate `{}` in app.builder (glade file)'.format(self.CONTAINER))
