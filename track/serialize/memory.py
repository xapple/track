"""
This module implements the in memory serialization.
"""

# Internal modules #
from track.seralize import Serializer

################################################################################
class SerializerMemory(Serializer):
    def __init__(self):
        self.tracks = []

    def defineFields(fields):
        self.fields = fields

    def newTrack(attributes):
        self.tracks.append({'info': attributes, 'features': []})

    def newFeature(feature):
        self.tracks[-1]['features'].append(feature)
