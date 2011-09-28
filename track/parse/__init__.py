"""
This subpackage contains one python source file per format implemented for parsing.
"""

# Built-in modules #
import sys

# Variables #
parsers = {
    'bed':   {'module': 'track.parse.bed',      'class': 'ParserBED'},
    'track': {'module': 'track.parse.instance', 'class': 'ParserTrack'},
}

################################################################################
def get_parser(path, format):
    """Given a path and a format will return the appropriate parser.

            * *path* is a string specifying the path of the track to parse.
            * *format* is a string specifying the format of the track to parse.

        Examples::

            import track.parse
            import track.serialze
            serializer = track.serialize.get_serializer('tmp/test.sql', 'sql')
            parser = track.parse.get_parser('tmp/test.bed', 'bed')
            parser(serializer)

        ``get_parser`` returns a Parser instance.
    """
    if not format in parsers: raise Exception("The format '" + format + "' is not supported.")
    info = parsers[format]
    # Import the objects #
    base_module    = __import__(info['module'])
    sub_module     = sys.modules[info['module']]
    class_object   = getattr(sub_module, info['class'])
    class_instance = class_object(path)
    # Return an instance #
    return class_instance

################################################################################
class Parser(object):
    def __init__(self, path):
        self.path = path

    def __call__(self, handler=None):
        # Default handler #
        if not handler:
            from track.seralize import Serializer
            handler = Serializer()
        # Enter the handler #
        with handler as self.handler:
            self.parse()
        # Return a list or a single element #
        if len(self.handler.tracks) == 1: return self.handler.tracks[0]
        else: return self.handler.tracks

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
