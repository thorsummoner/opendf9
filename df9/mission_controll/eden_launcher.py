"""
    Eden initial probe destination picker.
"""

from gi.repository import Gdk
from gi.repository import GdkPixbuf

from df9.mission_controll import MissionControll

class EdenLauncher(MissionControll):
    CONTAINER = 'eden'

    GALAXY_MAP_BG = 'df9/assets/images/author-eso/2048px-Wide_Field_Imager_view_of_a_Milky_Way_look-alike_NGC_6744.jpg'

    def __init__(self, app):
        super(EdenLauncher, self).__init__(app)

        # Load in gui elements that Glade can't handle AFAIK
        app.builder.get_object('eden_launch_overlay').add_overlay(
            app.builder.get_object('eden_launch')
        )

        # Load space image
        self.galaxy_map_bg = GdkPixbuf.Pixbuf.new_from_file(self.GALAXY_MAP_BG)

        # Connect drawing area to this class's handler
        app.builder.get_object('eden_drawingarea').connect(
            'draw',
            self.DrawingAreaHandler(self).draw,
        )

    class DrawingAreaHandler(object):
        def __init__(self, parent):
            super(EdenLauncher.DrawingAreaHandler, self).__init__()
            self.parent = parent

        def draw(self, widget, ct):
            width = widget.get_allocated_width()
            height = widget.get_allocated_height()

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
