"""
This subpackage contains one python source file per format implemented for parsing.
"""

from track.seralize.memory import SerializerMemory

################################################################################
class Parser(object):
    def __init__(self, path, handler=None):
        self.path = path
        if not handler: handler = SerializerMemory()
        self.handler = handler
