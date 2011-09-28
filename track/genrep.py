"""
This subpackage contains functions to access the GenRep server.
"""

# Built-in modules #
import urllib2, json

# Constants #
url = "http://bbcftools.vital-it.ch/genrep/"

################################################################################
def list_assemblies():
    """Returns a list of assemblies available on GenRep."""
    raw = urllib2.urlopen(url+"/assemblies.json")
    return [a['assembly'].get('name') for a in json.loads(raw)]

def get_assembly(assembly):
    """Get an Assembly object corresponding to *assembly*.

    *assembly* may be an integer giving the assembly ID, or a string giving the assembly name.
    """

################################################################################
class Assembly(object):
    """A representation of a GenRep assembly."""

    def __init__(self, info, key):
        self.__dict__.update(info[key])

    @property
    def chrmeta(self):
        """ Returns a dictionary of chromosome meta data looking something like:

            {'chr1': {'length': 249250621},
             'chr2': {'length': 135534747},
             'chr3': {'length': 135006516},

        """
        return dict([(v['name'], dict([('length', v['length'])])) for v in self.chromosomes.values()])
