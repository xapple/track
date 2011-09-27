"""
This subpackage contains one python source file per format implemented for parsing.
"""

# Built-in modules #
from track.seralize import Serializer

# Variables #
parsers = {
    'bed': {'module': 'track.parse.bed', 'class': 'ParserBED'},
}

################################################################################
def get_parser(path, format, handler=None):
    """Given a path, a format and a handler will return the appropriate parser.

            * *path* is a string specifying the path of the track to parse.
            * *format* is a string specifying the format of the track to parse.
            * *handler* is an instance on which the methods will be called.

        Examples::

            import track.parse
            import track.serialze
            serializer = track.serialize.get_serializer('tmp/test.sql', 'sql')
            parser = track.parse.get_parser('tmp/test.bed', 'bed', serializer)
            parser()

        ``parse`` returns a Parser instance.
    """
    if not format in parsers: raise Exception("The format '" + format + "' is not supported.")
    dct = parsers[format]
    mod = __import__(dct['module'])
    cls = getattr(mod, dct['class'])
    ins = cls(path, handler)
    return ins()

################################################################################
class Parser(object):
    def __init__(self, path, handler=None):
        self.path = path
        if not handler: handler = Serializer()
        self.handler = handler

    def __call__(self):
        self.parse()
        if len(self.handler.tracks) == 1: return self.handler.tracks[0]
        else: return self.handler.tracks
