#!/usr/bin/env python

"""
    Main Window Class
"""

import os
import signal

from gi.repository import Gtk
from gi.repository import Gdk

class Window(Gtk.Window):
    """
        Gui application interface.
    """
    # pylint: disable=no-member

    ROOT_WINDOW = 'window1'
    GLADE_FILE = None
    CSS_PROVIDER_FILE = None


    def __init__(self, *args):
        super(Window, self).__init__(*args)

        builder = Gtk.Builder()
        builder.add_from_file(self.GLADE_FILE)
        self.builder = builder
        self.window = self.builder.get_object(self.ROOT_WINDOW)
        self.builder.connect_signals(self.Handler(self))

        self.cssprovider = Gtk.CssProvider()
        self.cssprovider.load_from_path(self.CSS_PROVIDER_FILE)

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            self.cssprovider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.window.show_all()

    @staticmethod
    def replace_child(container, new_child):
        """
            Remove all elements from container and add an element
            to the container.
        """
        for child in container.get_children():
            container.remove(child)
        container.add(new_child)

    @staticmethod
    def main():
        """
            Gtk.main wrapper.
        """
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        Gtk.main()

    class BaseHandler(object):
        """
            Main Window Event Handler
        """

        def __init__(self, parent):
            super(Window.BaseHandler, self).__init__()
            self.parent = parent
            parent.window.connect("delete-event", self.on_delete_window)

        @staticmethod
        def on_delete_window(*args):
            """
                Window Close Action
            """
            Gtk.main_quit(*args)

    # pylint: enable=no-member


@staticmethod
def draw(widget, ct):
    """
        Draw Diagnostic Marks
    """
    width = widget.get_allocated_width()
    height = widget.get_allocated_height()
    ct.set_source_rgb(0, 0, 0)
    ct.move_to(0 * width, 0 * height)
    ct.line_to(1 * width, 1 * height)
    ct.move_to(1 * width, 0 * height)
    ct.line_to(0 * width, 1 * height)
    ct.set_line_width(20)
    ct.stroke()

    ct.rectangle(0*width, 0*height, 0.5*width, 0.5*height)
    ct.set_source_rgba(1, 0, 0, 0.80)
    ct.fill()

    ct.rectangle(0*width, 0.5*height, 0.5*width, 0.5*height)
    ct.set_source_rgba(0, 1, 0, 0.60)
    ct.fill()

    ct.rectangle(0.5*width, 0*height, 0.5*width, 0.5*height)
    ct.set_source_rgba(0, 0, 1, 0.40)
    ct.fill()
