"""
    Load png data from ora files
"""

import zipfile
import xml.etree.ElementTree as xml_object
from os import path
from StringIO import StringIO

import png as pypng

PYPNG_HEADERS = ('width', 'height', 'pixels', 'metadata')

#pylint: disable=R0903
class OraImage(object):
    """docstring for OraImage"""

    def __init__(self, file_path):
        super(OraImage, self).__init__()
        self.file_path = file_path
        self.name = path.splitext(path.basename(file_path))[0]

        self.zipfile = zipfile.ZipFile(file_path)
        self.metadata_stack = xml_object.fromstring(self.zipfile.read('stack.xml'))

        self.layers = dict()
        for layer in self.metadata_stack.iter('layer'):
            self.layers[layer.attrib['name']] = dict(zip(
                PYPNG_HEADERS,
                pypng.Reader(
                    file=StringIO(
                        self.zipfile.read(layer.attrib['src'])
                    )
                ).read()
            ))
            # Read generator into list, (so that reading it doesn't exhaust it)
            # This will probably need to change if used for big images
            self.layers[layer.attrib['name']]['pixels'] = list(
                self.layers[layer.attrib['name']]['pixels']
            )

        self.width = int(self.metadata_stack.attrib.get('w', ''))
        self.height = int(self.metadata_stack.attrib.get('h', ''))

