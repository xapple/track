"""
This subpackage contains one python source file per format implemented for serialization.
"""

# Built-in modules #
import sys

# Internal modules #
from track.genrep import Assembly

# Variables #
serializers = {
    'memory':   {'module': 'track.serialize.memory',   'class': 'SerializerMemory'},
    'sql':      {'module': 'track.serialize.sql',      'class': 'SerializerSQL'},
    'bed':      {'module': 'track.serialize.bed',      'class': 'SerializerBED'},
    'wig':      {'module': 'track.serialize.wig',      'class': 'SerializerWIG'},
    'gff':      {'module': 'track.serialize.gff',      'class': 'SerializerGFF'},
    'gtf':      {'module': 'track.serialize.gtf',      'class': 'SerializerGTF'},
    'bedgraph': {'module': 'track.serialize.bedgraph', 'class': 'SerializerBedgraph'},
    'bigwig':   {'module': 'track.serialize.bigwig',   'class': 'SerializerBigwig'},
}

################################################################################
def get_serializer(path, format):
    """Given a path and a format will return the appropriate serializer.

            * *path* is a string specifying the path of the track to parse.
            * *format* is a string specifying the format of the track to parse.

        Examples::

            import track.parse
            import track.serialze
            serializer = track.serialize.get_serializer('tmp/test.sql', 'sql')
            parser = track.parse.get_parser('tmp/test.bed', 'bed')
            parser(serializer)

        ``get_serializer`` returns a Serializer instance.
    """
    # Is the format supported ? #
    if not format in serializers: raise Exception("The format '%s' is not supported." % format)
    info = serializers[format]
    # Import the objects #
    base_module    = __import__(info['module'])
    sub_module     = sys.modules[info['module']]
    class_object   = getattr(sub_module, info['class'])
    class_instance = class_object(path)
    # Return an instance #
    return class_instance

################################################################################
class Serializer(object):
    def __init__(self, path):
        self.path = path
        self.tracks = []

    def __enter__(self):
        return self

    def __exit__(self, errtype, value, traceback):
        pass

    def __call__(self, parser):
        self.parser = parser

    def error(self, message, path=None, line_number=None):
        if path and line_number:       location = " '%s:%s'" % (path, line_number)
        elif path and not line_number: location = " '%s'"    % (path)
        else:                          location = ""
        raise Exception(message % location)

    def defineFields(self, fields):
        pass

    def defineChrmeta(self, chrmeta):
        self.chrmeta = chrmeta

    def defineAssembly(self, assembly):
        self.defineChrmeta(Assembly(assembly).chrmeta)

    def newTrack(self, info=None, name=None):
        pass

    def newFeature(self, chrom, feature):
        raise NotImplementedError

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
