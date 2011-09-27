"""
This subpackage contains one python source file per format implemented for serialization.
"""

# Variables #
serializers = {
    'sql': {'module': 'track.serialize.sql', 'class': 'SerializerSQL'},
}

################################################################################
def get_serializer(path, format, handler=None):
    """Given a path and a format will return the appropriate serializer.

            * *path* is a string specifying the path of the track to parse.
            * *format* is a string specifying the format of the track to parse.

        Examples::

            import track.parse
            import track.serialze
            serializer = track.serialize.get_serializer('tmp/test.sql', 'sql')
            parser = track.parse.get_parser('tmp/test.bed', 'bed', serializer)
            parser()

        ``serialize`` returns a Serializer instance.
    """
    if not format in parsers: raise Exception("The format '" + format + "' is not supported.")
    dct = parsers[format]
    mod = __import__(dct['module'])
    cls = getattr(mod, dct['class'])
    return cls(path, handler)

################################################################################
class Serializer(object):
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        return self

    def __exit__(self, errtype, value, traceback):
        pass

    def error(path, line_number, message):
        location = " '" + path + ":" + line_number + "'"
        raise Exception(message % location)

    def defineFields(fields):
        self.fields = fields

    def newTrack(attributes):
        self.tracks.append({'info': attributes, 'features': []})

    def newFeature(feature):
        self.tracks[-1]['features'].append(feature)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
