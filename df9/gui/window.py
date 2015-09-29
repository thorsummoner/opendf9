#!/usr/bin/env python

"""
    Main Window Class
"""

import signal

from gi.repository import Gtk
from gi.repository import Gdk

class Window(Gtk.Window):
    """
        Gui application interface.
    """
    # Gtk doesn't expose its memebers in a way pylint can understand.

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

        if self.CSS_PROVIDER_FILE is not None:
            self.cssprovider = Gtk.CssProvider()
            self.cssprovider.load_from_path(self.CSS_PROVIDER_FILE)

            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                self.cssprovider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

        self.window.show_all()

    @staticmethod
    def replace_child(gtk_container, widget):
        """
            Remove all children from a Gtk.Container,
            Then add `widget` to the cotnainer
        """
        for child in gtk_container.get_children():
            gtk_container.remove(child)
        print('segfault here')
        gtk_container.add(widget)

    @staticmethod
    def main():
        """
            Gtk.main wrapper.
        """
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        Gtk.main()

    #pylint: disable=R0903
    class Handler(object):
        """
            Base Main Window Event Handler
        """

        def __init__(self, parent):
            super(Window.Handler, self).__init__()
            self.parent = parent
            parent.window.connect("delete-event", self.on_delete_window)

        @staticmethod
        def on_delete_window(*args):
            """
                Window Close Action
            """
            Gtk.main_quit(*args)


@staticmethod
def draw(widget, cairo_ct):
    """
        Draw Diagnostic Marks
    """
    width = widget.get_allocated_width()
    height = widget.get_allocated_height()
    cairo_ct.set_source_rgb(0, 0, 0)
    cairo_ct.move_to(0 * width, 0 * height)
    cairo_ct.line_to(1 * width, 1 * height)
    cairo_ct.move_to(1 * width, 0 * height)
    cairo_ct.line_to(0 * width, 1 * height)
    cairo_ct.set_line_width(20)
    cairo_ct.stroke()

    cairo_ct.rectangle(0*width, 0*height, 0.5*width, 0.5*height)
    cairo_ct.set_source_rgba(1, 0, 0, 0.80)
    cairo_ct.fill()

    cairo_ct.rectangle(0*width, 0.5*height, 0.5*width, 0.5*height)
    cairo_ct.set_source_rgba(0, 1, 0, 0.60)
    cairo_ct.fill()

    cairo_ct.rectangle(0.5*width, 0*height, 0.5*width, 0.5*height)
    cairo_ct.set_source_rgba(0, 0, 1, 0.40)
    cairo_ct.fill()
