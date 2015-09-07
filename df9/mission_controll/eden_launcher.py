"""
    Eden initial probe destination picker.
"""

import math

from gi.repository import Gdk
from gi.repository import GdkPixbuf
import cairo

from df9.mission_controll import MissionControll
from df9.fontloader import FontLoader

FULL = 256.0

TEXT_EXTENTS_KEYS = ('x_bearing', 'y_bearing', 'width', 'height', 'x_advance', 'y_advance')
CELLS_WIDTH = 60
CELLS_HEIGHT = 60

UNIVERSE_SIZE = 28
UNIVERSE_METRIC = 'Billion Parsecs'
PARSEC_LIGHTYEAR = 3.262

ORIGINAL_COORD = (0.15116763695057492, 0.37949796350990855)

class EdenLauncher(MissionControll):
    CONTAINER = 'eden'

    GALAXY_MAP_BG = 'df9/assets/images/author-eso/2048px-Wide_Field_Imager_view_of_a_Milky_Way_look-alike_NGC_6744.jpg'
    FONT_FACE_FILE = 'df9/assets/fonts/ProFontWindows.ttf'
    FONT_FACE = FontLoader().cairo_font_face_from_file(FONT_FACE_FILE)

    cursor = True
    last_settlement = ORIGINAL_COORD
    selected_settlement = None
    grid = False

    _selected_coord = None

    def __init__(self, app):
        super(EdenLauncher, self).__init__(app)

        # Load in gui elements that Glade can't handle AFAIK
        app.builder.get_object('eden_launch_overlay').add_overlay(
            app.builder.get_object('eden_launch')
        )

        # Load space image
        self.galaxy_map_bg = GdkPixbuf.Pixbuf.new_from_file(self.GALAXY_MAP_BG)

        # Connect drawing area to this class's handler
        eden_drawingarea =  app.builder.get_object('eden_drawingarea')
        eden_drawingarea.set_events(
            Gdk.EventMask.POINTER_MOTION_MASK
            | Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
        )
        eden_drawing_handler = self.DrawingAreaHandler(self, app)
        eden_drawingarea.connect('draw', eden_drawing_handler.draw)

        eden_drawingarea.connect('motion_notify_event', eden_drawing_handler.motion_notify_event)
        eden_drawingarea.connect('button_release_event',  eden_drawing_handler.button_release_event)

        # Get data form elements
        self.eden_accept = app.builder.get_object('eden_accept')
        self.eden_sectors = app.builder.get_object('eden_sectors')
        self.eden_sectors.connect('toggled', self.grid_toggle)

        self.eden_x1 = app.builder.get_object('eden_x1')
        self.eden_y1 = app.builder.get_object('eden_y1')
        if 'last_settlement':
            self.last_parsec = self.get_parsec(*self.last_settlement)
            self.eden_x1.set_text('{:.11}'.format(self.last_parsec[0]))
            self.eden_y1.set_text('{:.11}'.format(self.last_parsec[1]))
        self.eden_x2 = app.builder.get_object('eden_x2')
        self.eden_y2 = app.builder.get_object('eden_y2')
        self.eden_distance = app.builder.get_object('eden_distance')
        self.eden_arrival = app.builder.get_object('eden_arrival')

    @property
    def selected_coord(self):
        return self._selected_coord

    @selected_coord.setter
    def selected_coord(self, value):
        self._selected_coord = self.get_cell(*value)
        self.selected_settlement = value
        self.cursor = False
        self.eden_accept.set_sensitive(True)

        parsec = self.get_parsec(*value)

        self.eden_x2.set_text('{:.11}'.format(parsec[0]))
        self.eden_y2.set_text('{:.11}'.format(parsec[1]))

        distance = math.sqrt(
            pow(parsec[0] - self.last_parsec[0], 2)
            + pow(parsec[1] - self.last_parsec[1], 2)
        )

        self.eden_distance.set_text(str(distance))
        self.eden_arrival.set_text(str(distance * PARSEC_LIGHTYEAR))



    def get_cell(self, cursor_percent_x, cursor_percent_y):
        cell_x = math.ceil(cursor_percent_x * CELLS_WIDTH)
        cell_y = math.ceil(cursor_percent_y * CELLS_HEIGHT)
        return (
            int(cell_x if cell_x > 0 else 1),
            int(cell_y if cell_y > 0 else 1),
        )

    def get_parsec(self, cursor_percent_x, cursor_percent_y):
        return (
            cursor_percent_x * UNIVERSE_SIZE,
            cursor_percent_y * UNIVERSE_SIZE,
        )

    def grid_toggle(self, widget):
        self.grid = widget.get_active()
        self.app.window.get_window().invalidate_rect(None, False)

    class DrawingAreaHandler(object):

        DIAGONAL_RATE = 0.49
        AMBER_ACCENT_SHIFT = 1
        COLOR_DARK_AMBER = (227/FULL, 98/FULL, 59/FULL)
        COLOR_AMBER = (242/FULL, 179/FULL, 69/FULL)
        COORDINATE_INFO_OFFSET = (-24, 10)
        COORD_X_OFF = 10
        COORD_Y_OFF = 48

        cursor_pos = None

        def __init__(self, parent, app):
            super(EdenLauncher.DrawingAreaHandler, self).__init__()

            self.parent = parent
            self.app = app

        def draw(self, widget, ct):
            width = widget.get_allocated_width()
            height = widget.get_allocated_height()

            cursor_x = 0
            cursor_y = 0
            try:
                cursor_x = self.cursor_pos.x
                cursor_y = self.cursor_pos.y
                # And reset
                self.cursor_pos = None
            except AttributeError, err:
                pass


            if 'universe':
                # Paint the universe
                img_width = float(self.parent.galaxy_map_bg.get_width())
                img_height = float(self.parent.galaxy_map_bg.get_height())
                # Scale
                width_ratio = width / img_width
                height_ratio = height / img_height
                scale_xy = max(height_ratio, width_ratio)
                # Center
                off_x =  (width  - round(img_width*scale_xy)) //2
                off_y =  (height - round(img_height*scale_xy)) //2

                # Paint
                ct.save()

                ct.translate(off_x, off_y)
                ct.scale(scale_xy, scale_xy)

                Gdk.cairo_set_source_pixbuf(ct, self.parent.galaxy_map_bg, 0, 0)
                ct.paint()

                ct.restore()

            if self.parent.grid:
                ct.set_source_rgba(
                    self.COLOR_AMBER[0],
                    self.COLOR_AMBER[1],
                    self.COLOR_AMBER[2],
                    0.1
                )
                width_step = width/60.0
                height_step = height/60.0
                for x in range(60):
                    ct.move_to(x*width_step, 0)
                    ct.line_to(x*width_step, height)
                for y in range(60):
                    ct.move_to(0, y*height_step)
                    ct.line_to(width, y*height_step)
                ct.stroke()

            if 'last_settlement':
                self._amber_marker(ct,
                    self.parent.last_settlement[0]*width,
                    self.parent.last_settlement[1]*height,
                )
            if self.parent.selected_settlement:
                self._amber_marker(ct,
                    self.parent.selected_settlement[0]*width,
                    self.parent.selected_settlement[1]*height,
                )
                ct.set_dash([14.0, 6.0])
                self._amber_line(
                    ct,
                    self.parent.last_settlement[0]*width,
                    self.parent.last_settlement[1]*height,
                    self.parent.selected_settlement[0]*width,
                    self.parent.selected_settlement[1]*height,
                )
                ct.set_dash([])


            if self.parent.cursor and cursor_y > 0 and cursor_x > 0:
                # Paint a cursor, Vertical Line
                self._amber_line(ct, cursor_x, 0, cursor_x, height)

                # Paint a cursor, Diagonal Line
                self._amber_line(
                    ct,
                    0, cursor_y - (cursor_x * self.DIAGONAL_RATE),
                    width, cursor_y + ((width - cursor_x) * self.DIAGONAL_RATE)
                )
                # Dashed counter-diagonal line
                ct.set_dash([14.0, 6.0])
                self._amber_line(
                    ct,
                    cursor_x-width, cursor_y + (width * self.DIAGONAL_RATE),
                     cursor_x+width, cursor_y - (width * self.DIAGONAL_RATE)
                )
                ct.set_dash([])

                if 'coordinate_info_offset':
                    ct.set_font_face(self.parent.FONT_FACE)

                    ct.set_font_size(20)
                    text_coord = "({:>2}, {:>2})".format(*self.parent.get_cell(
                        cursor_x / width,
                        cursor_y / height
                    ))
                    text_coord_extents = dict(zip(
                        TEXT_EXTENTS_KEYS,
                        ct.text_extents(text_coord)
                    ))

                    text_coord_x = cursor_x - text_coord_extents['width']
                    text_coord_y = cursor_y + text_coord_extents['height']
                    self._amber_text(ct,
                        (text_coord_x - self.COORD_X_OFF if text_coord_x - self.COORD_X_OFF > 10 else cursor_x + self.COORD_X_OFF),
                        (text_coord_y + self.COORD_Y_OFF if text_coord_y + self.COORD_Y_OFF < height - 10 else cursor_y - self.COORD_Y_OFF),
                        text_coord
                    )

        def _amber_line(self, ct, x1, y1, x2, y2):
            """
                Stroke a two-tone line.
            """

            ct.set_source_rgba(1, 1, 1, 0.5)
            ct.set_line_width(2.2)
            ct.move_to(x1+self.AMBER_ACCENT_SHIFT/2.0, y1+self.AMBER_ACCENT_SHIFT/2.0)
            ct.line_to(x2+self.AMBER_ACCENT_SHIFT/2.0, y2+self.AMBER_ACCENT_SHIFT/2.0)
            ct.stroke()

            ct.set_source_rgb(*self.COLOR_DARK_AMBER)
            ct.set_line_width(1.4)
            ct.move_to(x1+self.AMBER_ACCENT_SHIFT, y1+self.AMBER_ACCENT_SHIFT)
            ct.line_to(x2+self.AMBER_ACCENT_SHIFT, y2+self.AMBER_ACCENT_SHIFT)
            ct.stroke()

            ct.set_source_rgb(*self.COLOR_AMBER)
            ct.set_line_width(1)
            ct.move_to(x1, y1)
            ct.line_to(x2, y2)
            ct.stroke()

        def _amber_text(self, ct, x, y, msg):
            ct.set_source_rgb(*self.COLOR_DARK_AMBER)
            ct.move_to(x+self.AMBER_ACCENT_SHIFT, y+self.AMBER_ACCENT_SHIFT)
            ct.show_text(msg)

            ct.set_source_rgb(*self.COLOR_AMBER)
            ct.move_to(x, y)
            ct.show_text(msg)

        def _amber_marker(self, ct, x, y):
            ct.set_source_rgb(*self.COLOR_DARK_AMBER)
            ct.arc(x, y, 3, 0, 2*math.pi)
            ct.fill()
            ct.set_source_rgb(*self.COLOR_AMBER)
            ct.arc(x+self.AMBER_ACCENT_SHIFT, y+self.AMBER_ACCENT_SHIFT, 3, 0, 2*math.pi)
            ct.fill()
            self._amber_line(ct, x, y, x-8, y-8)
            self._amber_line(ct, x, y, x+8, y-8)
            self._amber_line(ct, x, y, x, y-24)

        def motion_notify_event(self, widget, event):
            """
                Update cursor position, (event.{x,y}) and repaint view.
            """
            self.cursor_pos = event
            self.app.window.get_window().invalidate_rect(None, False)

        def button_release_event(self, widget, event):
            width = widget.get_allocated_width()
            height = widget.get_allocated_height()

            if self.parent.cursor:
                self.parent.selected_coord = (event.x/width, event.y/height)
            self.app.window.get_window().invalidate_rect(None, False)
