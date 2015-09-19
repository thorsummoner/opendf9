"""
    Eden initial probe destination picker.
"""

import math
from collections import namedtuple

from gi.repository import Gdk
from gi.repository import GdkPixbuf

from df9.mission_controll import MissionControll
from df9.fontloader import FontLoader
from df9.oraimage import OraImage

FULL = 256.0

TEXT_EXTENTS_KEYS = ('x_bearing', 'y_bearing', 'width', 'height', 'x_advance', 'y_advance')
CELLS_WIDTH = 60
CELLS_HEIGHT = 60

UNIVERSE_SIZE = 28
UNIVERSE_METRIC = 'Billion Parsecs'
PARSEC_LIGHTYEAR = 3.262

ORIGINAL_COORD = (0.15116763695057492, 0.37949796350990855)

Coordinate = namedtuple('Coordinate', ['x', 'y'])

class EdenLauncher(MissionControll):
    """
        New game starting conditions screen
    """
    CONTAINER = 'eden'

    GALAXY_MAP_BG = 'df9/assets/images/author-eso/' \
        + '2048px-Wide_Field_Imager_view_of_a_Milky_Way_look-alike_NGC_6744.jpg'
    FONT_FACE_FILE = 'df9/assets/fonts/ProFontWindows.ttf'
    FONT_FACE = FontLoader().cairo_font_face_from_file(FONT_FACE_FILE)
    REGIONAL_FACTORS_FILE = 'df9/assets/eden/noise-stack.ora'

    #pylint: disable=C0326
    REGIONAL_FACTORS = (
        {'name': 'Stellar Density',       'key': 'density'},
        {'name': 'Warpgate Proximity',    'key': 'warp'},
        {'name': 'Threat Factor',         'key': 'threat'},
        {'name': 'Magnetic Interference', 'key': 'interference'},
    )
    #pylint: enable=C0326

    cursor = True
    last_settlement = ORIGINAL_COORD
    selected_settlement = None
    grid = False

    _selected_coord = None

    def __init__(self, app):
        super(EdenLauncher, self).__init__(app)

        # Load in gui elements that Glade can't handle AFAIK
        self.eden_launch = app.builder.get_object('eden_launch')
        app.builder.get_object('eden_launch_overlay').add_overlay(
            self.eden_launch
        )

        # Load space image
        self.galaxy_map_bg = GdkPixbuf.Pixbuf.new_from_file(self.GALAXY_MAP_BG)

        # Connect drawing area to this class's handler
        eden_drawingarea = app.builder.get_object('eden_drawingarea')
        eden_drawingarea.set_events(
            Gdk.EventMask.POINTER_MOTION_MASK
            | Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
        )
        eden_drawing_handler = self.DrawingAreaHandler(self, app)
        eden_drawingarea.connect('draw', eden_drawing_handler.draw)

        eden_drawingarea.connect('motion_notify_event', eden_drawing_handler.motion_notify_event)
        eden_drawingarea.connect('button_release_event', eden_drawing_handler.button_release_event)

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

        self.eden_accept_accept = app.builder.get_object('eden_accept_accept')
        self.eden_accept_accept.connect('clicked', self.on_eden_accept_accept)
        self.eden_accept_cancel = app.builder.get_object('eden_accept_cancel')
        self.eden_accept_cancel.connect('clicked', self.on_eden_accept_cancel)
        self.eden_accept_neutral = app.builder.get_object('eden_accept_neutral')

        self.eden_launch_launch = app.builder.get_object('eden_launch_launch')
        self.eden_launch_launch.connect('clicked', self.on_eden_launch_launch)
        self.eden_launch_cancel = app.builder.get_object('eden_launch_cancel')
        self.eden_launch_cancel.connect('button_press_event', self.on_eden_launch_cancel)

        # Load Regional Data
        self.regional_factors_data = OraImage(self.REGIONAL_FACTORS_FILE)

    @property
    def selected_coord(self):
        """
            Selected cell
        """
        return self._selected_coord

    @selected_coord.setter
    def selected_coord(self, value):
        """
            When selecting a cell, ui elements are updated
        """
        if value:
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

        else:
            self._selected_coord = None
            self.selected_settlement = None
            self.cursor = True
            self.eden_accept.set_sensitive(False)
            self.eden_accept_neutral.set_active(True)
            self.app.window.get_window().invalidate_rect(None, False)

            self.eden_x2.set_text('')
            self.eden_y2.set_text('')
            self.eden_distance.set_text('')
            self.eden_arrival.set_text('')

    @staticmethod
    def get_cell(cursor_percent_x, cursor_percent_y):
        """
            Return grid cell for percent
        """
        cell_x = math.ceil(cursor_percent_x * CELLS_WIDTH)
        cell_y = math.ceil(cursor_percent_y * CELLS_HEIGHT)
        return (
            int(cell_x if cell_x > 0 else 1),
            int(cell_y if cell_y > 0 else 1),
        )

    @staticmethod
    def get_parsec(cursor_percent_x, cursor_percent_y):
        """
            Return distance in Parsecs from top left (0, 0) of universe
        """
        return (
            cursor_percent_x * UNIVERSE_SIZE,
            cursor_percent_y * UNIVERSE_SIZE,
        )

    def grid_toggle(self, widget):
        """
            Toggle painted element and redraw.
        """
        self.grid = widget.get_active()
        self.app.window.get_window().invalidate_rect(None, False)

    def on_eden_accept_accept(self, *_):
        """ on_eden_accept_accept """
        self.eden_accept.set_sensitive(False)
        self.eden_launch.set_sensitive(True)

    def on_eden_accept_cancel(self, *_):
        """ on_eden_accept_cancel """
        self.selected_coord = None

    def on_eden_launch_launch(self, *_):
        """ on_eden_launch_launch """
        self.app.replace_mission_controll(self.app.loadingscreen)

    def on_eden_launch_cancel(self, *_):
        """ on_eden_launch_cancel """
        self.selected_coord = None
        self.eden_launch.set_sensitive(False)

    class DrawingAreaHandler(object):
        """
            Handle draw events of drawingarea
        """

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

        def draw(self, widget, cairo_ct):
            width = widget.get_allocated_width()
            height = widget.get_allocated_height()

            cursor_x = 0
            cursor_y = 0
            try:
                cursor_x = self.cursor_pos.x
                cursor_y = self.cursor_pos.y
                # And reset
                self.cursor_pos = None
            except AttributeError:
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
                off_x = (width  - round(img_width*scale_xy)) //2
                off_y = (height - round(img_height*scale_xy)) //2

                # Paint
                cairo_ct.save()

                cairo_ct.translate(off_x, off_y)
                cairo_ct.scale(scale_xy, scale_xy)

                Gdk.cairo_set_source_pixbuf(cairo_ct, self.parent.galaxy_map_bg, 0, 0)
                cairo_ct.paint()

                cairo_ct.restore()

            if self.parent.grid:
                cairo_ct.set_source_rgba(
                    self.COLOR_AMBER[0],
                    self.COLOR_AMBER[1],
                    self.COLOR_AMBER[2],
                    0.1
                )
                width_step = width/60.0
                height_step = height/60.0
                for grid_x in range(60):
                    cairo_ct.move_to(grid_x*width_step, 0)
                    cairo_ct.line_to(grid_x*width_step, height)
                for grid_y in range(60):
                    cairo_ct.move_to(0, grid_y*height_step)
                    cairo_ct.line_to(width, grid_y*height_step)
                cairo_ct.stroke()

            if 'last_settlement':
                self._amber_marker(
                    cairo_ct,
                    self.parent.last_settlement[0]*width,
                    self.parent.last_settlement[1]*height,
                )
            if self.parent.selected_settlement:
                self._amber_marker(
                    cairo_ct,
                    self.parent.selected_settlement[0]*width,
                    self.parent.selected_settlement[1]*height,
                )
                cairo_ct.set_dash([14.0, 6.0])
                self._amber_line(
                    cairo_ct,
                    self.parent.last_settlement[0]*width,
                    self.parent.last_settlement[1]*height,
                    self.parent.selected_settlement[0]*width,
                    self.parent.selected_settlement[1]*height,
                )
                cairo_ct.set_dash([])


            if self.parent.cursor and cursor_y > 0 and cursor_x > 0:
                # Paint a cursor, Vertical Line
                self._amber_line(cairo_ct, cursor_x, 0, cursor_x, height)

                # Paint a cursor, Diagonal Line
                self._amber_line(
                    cairo_ct,
                    0, cursor_y - (cursor_x * self.DIAGONAL_RATE),
                    width, cursor_y + ((width - cursor_x) * self.DIAGONAL_RATE)
                )
                # Dashed counter-diagonal line
                cairo_ct.set_dash([14.0, 6.0])
                self._amber_line(
                    cairo_ct,
                    cursor_x-width, cursor_y + (width * self.DIAGONAL_RATE),
                    cursor_x+width, cursor_y - (width * self.DIAGONAL_RATE)
                )
                cairo_ct.set_dash([])

                coord = list(self.parent.get_cell(
                    cursor_x / width,
                    cursor_y / height
                ))
                coord[0] = (coord[0] if 0 < coord[0] < CELLS_WIDTH else 0)
                coord[1] = (coord[1] if 0 < coord[1] < CELLS_HEIGHT else 0)

                if 'coordinate_info_offset':
                    cairo_ct.set_font_face(self.parent.FONT_FACE)

                    cairo_ct.set_font_size(20)
                    text_coord = "({:>2}, {:>2})".format(*coord)
                    text_coord_extents = dict(zip(
                        TEXT_EXTENTS_KEYS,
                        cairo_ct.text_extents(text_coord)
                    ))

                    text_coord_x = cursor_x - text_coord_extents['width']
                    text_coord_y = cursor_y + text_coord_extents['height']
                    self._amber_text(
                        cairo_ct,
                        (
                            text_coord_x - self.COORD_X_OFF
                            if text_coord_x - self.COORD_X_OFF > 10
                            else cursor_x + self.COORD_X_OFF
                        ),
                        (
                            text_coord_y + self.COORD_Y_OFF
                            if text_coord_y + self.COORD_Y_OFF < height - 10
                            else cursor_y - self.COORD_Y_OFF
                        ),
                        text_coord
                    )
                if 'regional_factors':
                    line_step = 24
                    line = 0
                    for factor in self.parent.REGIONAL_FACTORS:
                        line += line_step
                        self._amber_text(
                            cairo_ct, 10, line,
                            '{:>21}: {:.3}'.format(
                                factor['name'],
                                self.parent.regional_factors_data.layers[
                                    factor['key']
                                ]['pixels'][coord[0]][coord[1]] / FULL
                            )
                        )


        def _amber_line(self, cairo_ct, x1, y1, x2, y2):
            """
                Stroke a two-tone line.
            """

            cairo_ct.set_source_rgba(1, 1, 1, 0.5)
            cairo_ct.set_line_width(2.2)
            cairo_ct.move_to(x1+self.AMBER_ACCENT_SHIFT/2.0, y1+self.AMBER_ACCENT_SHIFT/2.0)
            cairo_ct.line_to(x2+self.AMBER_ACCENT_SHIFT/2.0, y2+self.AMBER_ACCENT_SHIFT/2.0)
            cairo_ct.stroke()

            cairo_ct.set_source_rgb(*self.COLOR_DARK_AMBER)
            cairo_ct.set_line_width(1.4)
            cairo_ct.move_to(x1+self.AMBER_ACCENT_SHIFT, y1+self.AMBER_ACCENT_SHIFT)
            cairo_ct.line_to(x2+self.AMBER_ACCENT_SHIFT, y2+self.AMBER_ACCENT_SHIFT)
            cairo_ct.stroke()

            cairo_ct.set_source_rgb(*self.COLOR_AMBER)
            cairo_ct.set_line_width(1)
            cairo_ct.move_to(x1, y1)
            cairo_ct.line_to(x2, y2)
            cairo_ct.stroke()

        def _amber_text(self, cairo_ct, coord_x, coord_y, msg):
            """
                Sylized text painter
            """
            cairo_ct.set_source_rgb(*self.COLOR_DARK_AMBER)
            cairo_ct.move_to(coord_x+self.AMBER_ACCENT_SHIFT, coord_y+self.AMBER_ACCENT_SHIFT)
            cairo_ct.show_text(msg)

            cairo_ct.set_source_rgb(*self.COLOR_AMBER)
            cairo_ct.move_to(coord_x, coord_y)
            cairo_ct.show_text(msg)

        def _amber_marker(self, cairo_ct, coord_x, coord_y):
            """
                Stylized coordinate marker
            """
            cairo_ct.set_source_rgb(*self.COLOR_DARK_AMBER)
            cairo_ct.arc(coord_x, coord_y, 3, 0, 2*math.pi)
            cairo_ct.fill()
            cairo_ct.set_source_rgb(*self.COLOR_AMBER)
            cairo_ct.arc(
                coord_x+self.AMBER_ACCENT_SHIFT,
                coord_y+self.AMBER_ACCENT_SHIFT,
                3, 0, 2*math.pi
            )
            cairo_ct.fill()
            self._amber_line(cairo_ct, coord_x, coord_y, coord_x-8, coord_y-8)
            self._amber_line(cairo_ct, coord_x, coord_y, coord_x+8, coord_y-8)
            self._amber_line(cairo_ct, coord_x, coord_y, coord_x, coord_y-24)

        def motion_notify_event(self, _, event):
            """
                Update cursor position, (event.{x,y}) and repaint view.
            """
            self.cursor_pos = event
            self.app.window.get_window().invalidate_rect(None, False)

        def button_release_event(self, widget, event):
            """
                User selected point in universe
            """
            width = widget.get_allocated_width()
            height = widget.get_allocated_height()

            if self.parent.cursor:
                self.parent.selected_coord = (event.x/width, event.y/height)
            self.app.window.get_window().invalidate_rect(None, False)
