"""
    http://cairographics.org/freetypepython/
"""

import ctypes
import cairo

CAIRO_STATUS_SUCCESS = 0
FT_Err_Ok = 0

class PycairoContext(ctypes.Structure):
    _fields_ = [('PyObject_HEAD', ctypes.c_byte * object.__basicsize__),
        ('ctx', ctypes.c_void_p),
        ('base', ctypes.c_void_p)]

class FontLoader(object):
    """docstring for FontLoader"""

    _freetype_so = None
    _cairo_so = None
    _ft_lib = None
    _surface = None

    def __init__(self):
        super(FontLoader, self).__init__()

        # find shared objects
        self._freetype_so = ctypes.CDLL ('libfreetype.so.6')
        self._cairo_so = ctypes.CDLL ('libcairo.so.2')

        self._cairo_so.cairo_ft_font_face_create_for_ft_face.restype = ctypes.c_void_p
        self._cairo_so.cairo_ft_font_face_create_for_ft_face.argtypes = [ ctypes.c_void_p, ctypes.c_int ]
        self._cairo_so.cairo_set_font_face.argtypes = [ ctypes.c_void_p, ctypes.c_void_p ]
        self._cairo_so.cairo_font_face_status.argtypes = [ ctypes.c_void_p ]
        self._cairo_so.cairo_status.argtypes = [ ctypes.c_void_p ]

        # initialize freetype
        self._ft_lib = ctypes.c_void_p ()
        if FT_Err_Ok != self._freetype_so.FT_Init_FreeType (ctypes.byref (self._ft_lib)):
          raise RuntimeError('Error initialising FreeType library.')

        self._surface = cairo.ImageSurface (cairo.FORMAT_A8, 0, 0)

    def cairo_font_face_from_file(self, filename, faceindex=0, loadoptions=0):
        # create freetype face
        ft_face = ctypes.c_void_p()
        cairo_ctx = cairo.Context (self._surface)
        cairo_t = PycairoContext.from_address(id(cairo_ctx)).ctx

        if FT_Err_Ok != self._freetype_so.FT_New_Face (self._ft_lib, filename, faceindex, ctypes.byref(ft_face)):
            raise Exception('Error creating FreeType font face for ' + filename)

        # create cairo font face for freetype face
        cr_face = self._cairo_so.cairo_ft_font_face_create_for_ft_face (ft_face, loadoptions)
        if CAIRO_STATUS_SUCCESS != self._cairo_so.cairo_font_face_status (cr_face):
            raise Exception('Error creating cairo font face for ' + filename)

        self._cairo_so.cairo_set_font_face (cairo_t, cr_face)
        if CAIRO_STATUS_SUCCESS != self._cairo_so.cairo_status (cairo_t):
            raise Exception('Error creating cairo font face for ' + filename)

        face = cairo_ctx.get_font_face ()

        return face

def example():
    """
        Example font loading.
    """
    face = FontLoader().cairo_font_face_from_file('df9/assets/fonts/ProFontWindows.ttf', 0)

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 128, 128)

    ctx = cairo.Context(surface)

    ctx.set_font_face(face)
    ctx.set_font_size(30)
    ctx.move_to(0, 44)
    ctx.show_text('Hello,')

    ctx.move_to(30, 74)
    ctx.show_text('world!')

    del ctx

    surface.write_to_png('hello.png')
