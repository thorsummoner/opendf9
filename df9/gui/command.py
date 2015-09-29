"""
    Command Container
"""


from gi.repository import Gtk

class Command(Gtk.Container):
    """
        Interchangable container
    """

    GLADE_FILE = None
    CSS_PROVIDER_FILE = None
    MAIN_CONTAINER = None

    _main_container = None

    def __init__(self):
        super(Command, self).__init__()

        self._main_container = (
            self.MAIN_CONTAINER
            if self.MAIN_CONTAINER is not None
            else self.__class__.__name__
        )

        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.GLADE_FILE)
        self.window = self.builder.get_object(self.MAIN_CONTAINER)
        self.builder.connect_signals(self.Handler(self))

        if self.CSS_PROVIDER_FILE is not None:
            self.cssprovider = Gtk.CssProvider()
            self.cssprovider.load_from_path(self.CSS_PROVIDER_FILE)

            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                self.cssprovider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def replace_command(self, command):
        """
            Replace `self` with `command`
        """
        self.replace_child(self.get_parent(), command)


    class BaseHandler(object):
        """
            Main Window Event Handler
        """

        def __init__(self, parent):
            super(Window.BaseHandler, self).__init__()
            self.parent = parent
