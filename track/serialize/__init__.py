"""
This subpackage contains one python source file per format implemented for serialization.
"""

################################################################################
class Serializer(object):
    def error(path, line_number, message):
        location = " '" + path + ":" + line_number + "'"
        raise Exception(message % location)
    def defineFields(fields): pass
    def newTrack(attributes): pass
    def newFeature(feature): pass
    def endFile(feature): pass
