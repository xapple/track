"""
This module provides an interface to `GenRep <http://bbcftools.vital-it.ch/genrep/>`_ data source.
The ``Assembly`` class provides a representation of a particular entry in GenRep.
"""

# Built-in modules #
import urllib2, json

# Internal modules #
from track.common import property_cached

# Constants #
default_url = 'http://bbcftools.vital-it.ch/genrep/'

################################################################################
class Assembly(object):
    """Get an Assembly object corresponding to *assembly*.

    *assembly* may be an integer giving the assembly ID,
               or a string giving the assembly name,
               or a dictionary describing the species
               or an object describing the species.
    """

    def __init__(self, assembly):
        # Can be several types #
        if isinstance(assembly, int):          suffix = "id=%s"  % assembly
        elif isinstance(assembly, basestring): suffix = "name=%s"  % assembly
        elif isinstance(assembly, dict):       suffix = "name=%s"  % assembly['name']
        else:                                  suffix = "name=%s"  % assembly.name
        # Download data #
        info = json.loads(urllib2.urlopen(default_url + "assemblies.json?assembly_"  + suffix).read())
        # Update the self attributes with info data #
        self.json = info[0]['assembly']
        self.__dict__.update(self.json)

    @property_cached
    def chromosomes(self):
        """A list of chromsome dicitonaries."""
        address = default_url + "chromosomes.json?assembly_name=" + self.name
        info = json.loads(urllib2.urlopen(address).read())
        return [item['chromosome'] for item in info]

    @property_cached
    def chrmeta(self):
        """A dictionary of chromosome metadata::

            >>> from track import genrep
            >>> a = genrep.Assembly('TAIR10')
            >>> print a.chrmeta
            {'c': {'length': 154478}, 'm': {'length': 366924}, '1': {'length': 30427671}, '3': {'length': 23459830}, '2': {'length': 19698289}, '5': {'length': 26975502}, '4': {'length': 18585056}}
        """
        def get_name(chrom):
            other_names = [x['chr_name'] for x in chrom['chr_names']]
            other_names = [x['value'] for x in other_names if x['assembly_id']==self.id]
            if other_names: return other_names[0].encode('ascii')
            else: return chrom['name']
        def get_length(chrom):
            return chrom['length']
        return dict([(get_name(chrom), dict([('length', get_length(chrom))])) for chrom in self.chromosomes])

    def guess_chromosome_name(self, chromosome_name):
        """Searches the assembly for chromosome synonym names,
           and returns the canonical name of the chromosome.
           Returns None if the chromosome is not known about.

           :param chromosome_name: Any given name for a chromosome in this assembly.
           :type  chromosome_name: string

           :returns: The same or an other name for the chromosome.

           ::

               >>> from track import genrep
               >>> a = genrep.Assembly('sacCer2')
               >>> print a.guess_chromosome_name('chrR')
               2micron
        """
        address = default_url + "chromosomes.json?assembly_name=" + self.name + "&identifier=" + chromosome_name
        info = json.loads(urllib2.urlopen(address).read())
        if len(info) != 1: return None
        other_names = [x['chr_name'] for x in info[0]['chromosome']['chr_names']]
        return [x['value'] for x in other_names if x['assembly_id']==self.id][0].encode('ascii')

################################################################################
if __name__ == "__main__":
    import doctest
    doctest.testmod()
