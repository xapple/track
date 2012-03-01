"""
All manipulations
-----------------
"""

# Built-in modules #
import sys, types, pkgutil, sqlite3

# Internal modules #
import track
from track import manips, Track, FeatureStream
from track.extras import TrackCollection, VirtualTrack
from track.common import import_module, collapse, andify_strings

# Constants #
base_attributes = ['label', 'short_name', 'long_name', 'input_tracks', 'input_args',
                   'input_meta', 'output_tracks', 'tracks_collapse', 'chroms_collapse',
                   'fields_collapse', 'tooltip', 'numeric_example', 'visual_example',
                   'tests']
base_functions = ['generate']

# Conveniance functions #
is_gen   = lambda x: isinstance(x, sqlite3.Cursor) or \
                     isinstance(x, FeatureStream) or \
                     isinstance(x, types.GeneratorType) or \
                     isinstance(x, type(iter(()))) or \
                     isinstance(x, type(iter([])))
is_list  = lambda x: isinstance(x, tuple) or \
                     isinstance(x, list)
is_track = lambda x: isinstance(x, Track) or \
                     isinstance(x, TrackCollection) or \
                     isinstance(x, VirtualTrack)

################################################################################
class Manipulation(object):
    def __init__(self, *args):
        """Taking the module object of a standard manipulation file
            will build a callable instance satisfying the three
            access methods:

                1) overlap('tracks/pol2.sql', 'tracks/rap1.sql') # returns a virtual track
                2) overlap(pol2,rap1) # returns a virtual track
                3) overlap(pol2.read(chrom), rap1.read(chrom)) # returns a generator

            Other special cases:

                1) window_smoothing(pol2,rap1,L=100)
                2) merge_scores([pol2,rap1,ifhl,fhl1])
                3) overlap(pol2,rap1,ifhl,fhl1)
                4) complement(pol2.read(chrom), l=pol2.chrmeta[chrom]['length'])
        """
        # Only one argument #
        self.module = args[0]
        # Module attributes become instance attributes #
        for attr in base_attributes + base_functions: setattr(self, attr, getattr(self.module,attr))
        # Update the documentation #
        self.__doc__ = self.documentation

    @property
    def documentation(self):
        """Generate the sphinx docstring from the attributes of the manipulation."""
        # The long title #
        msg = self.long_name + "."
        # The tool tip #
        msg += "\n\n" + self.tooltip + '\n'
        # The input tracks #
        for t in self.input_tracks:
            if t.get('kind') == 'many':
                sub_msg = "\n:param %s: An arbitrary number of tracks or paths to tracks." \
                          " Eventually, generators yielding features."
            else:
                sub_msg = "\n:param %s: A track or the path to a track. Eventually, a generator yielding features."
            sub_msg = sub_msg % t['key']
            if 'fields' in t:
                if t.get('kind')=='many': sub_msg += " The fields read form these tracks will be: ``%s``"
                else:                     sub_msg += " The fields read form this track will be: ``%s``"
                sub_msg = sub_msg % t['fields']
                if '...' in t['fields']: sub_msg += ", extra fields will be used."
                else:                    sub_msg += ", extra fields will not be used."
            if t.get('no-overlap'): sub_msg += " The track is assumed to have no overlapping features."
            msg += sub_msg + '\n'
            if t.get('kind') == 'many': msg += ":type %s: list\n" % t['key']
        # The arguments #
        for p in self.input_args:
            msg += ":param %s:" % p['key']
            if 'doc' in p: msg += " " + p['doc']
            if 'default' in p: msg += " By default ``%s``." % p['default']
            if 'type' in p: msg += "\n:type %s: %s" % (p['key'], p['type'].__name__)
            msg += '\n'
        # The special parameter #
        for p in self.input_meta:
            msg += "\n:param %s:" % p['key']
            if 'kind' in p and p['kind'] == 'chrom_len':
                msg += " The length of the current chromosome " \
                       "(only necessary when calling the manipulation with generators).\n" \
                       ":type %s: int" % p['key']
            msg += '\n'
        # The output #
        for t in self.output_tracks:
            if 'fields' in t: msg += ":returns: A virtual track with the following fields: ``%s``." % t['fields']
            else:             msg += ":returns: A virtual track."
            msg += '\n'
        # The numeric example #
        if self.numeric_example:
            msg += '\nA numerical example::\n %s\n' % self.numeric_example.replace('\n','\n     ')
        # The viusal example #
        if self.visual_example:
            msg += '\nA visual example::\n %s\n' % self.visual_example.replace('\n','\n    ')
        # Chromosomes collapse #
        if self.chroms_collapse: msg += "\n"\
        "If the list of chromosomes contained in the various tracks differ," \
        " the conflict will be resolved by applying the '%s' principle." \
        % self.chroms_collapse
        # Tracks collapse #
        if self.tracks_collapse: msg += "\n"\
        "If the list of tracks supplied is more than the two authorized," \
        " the conflict will be resolved by applying the '%s' principle." \
        % self.tracks_collapse
        # Return the message #
        return msg

    def test(self):
        """Runs all unittest. Yields *got* and *expected*"""
        for test in self.tests:
            # Call the manipulation #
            final_args = {}
            for d in (test.get('tracks',{}), test.get('args',{})): final_args.update(d)
            result = self(**final_args)
            # In case we have a generator #
            if is_gen(result): got = list(result)
            # In case we have a track #
            if is_track(result):
                if 'chromosome' in test: got = list(result.read(test['chromosome']))
                else:                    got = list(result.read())
                result.close()
            # Return two elements #
            got = [tuple(x) for x in got]
            yield got, test['expected']

    def __call__(self, *args, **kwargs):
        """Check that all arguments are present
           and load all tracks that are given as paths
           instead of track objects. Also checks for
           direct calls with generators."""
        # Initialization #
        generator_call   = False # Special switch for direct generator calls
        found_args       = {}    # Will contain a set of parameters extracted
        found_tracks     = {}    # Will contain a set of track parameters extracted
        found_generators = {}    # Will contain a set of FeatureStream
        extra_args       = {}    # Will contain a set of parameters computed
        all_tracks       = []    # Will contain all single tracks sent
        tracks_to_close  = []    # Will contain single tracks to close
        virtual_tracks   = []    # Will contain the results tracks
        rest_of_fields   = []    # Will contain variable output fields when required
        ### Parse arguments ###
        for p in self.input_args:
            if p['key'] in kwargs: value = kwargs[p['key']]
            elif len(args) >= p['position']: value = args[p['position']-1]
            elif 'default' in p: value = p['default']
            elif p.get('optional'): continue
            else: raise Exception("The argument '%s' is missing for the manipulation '%s'." \
                                  % (p['key'], self.short_name))
            # Cast it if it's not the right type #
            if not isinstance(value, p['type']): value = p['type'](value)
            # Add it to the dict #
            found_args[p['key']] = value
        ### Parse tracks ###
        for t in self.input_tracks:
            if t['key'] in kwargs: value = kwargs[t['key']]
            elif len(args) >= t['position']: value = args[t['position']-1]
            elif 'default' in t: value = t['default']
            elif t.get('optional'): continue
            else: raise Exception("The argument '%s' is missing for the manipulation '%s'." \
                                  % (t['key'], self.short_name))
            # Check is track collection #
            if t.get('kind') == 'many':
                if not is_list(value):
                    message = "The track collection '%s' for the manipulation '%s' is not a list: %s"
                    raise Exception(message % (t['key'], self.short_name, value))
            # Don't modify the input list #
            if t.get('kind') == 'many': value = value[:]
            # Check for generator case #
            if is_gen(value): generator_call = True
            if t.get('kind') == 'many' and is_gen(value[0]): generator_call = True
            if generator_call:
                found_tracks[t['key']] = value
                continue
            # Check is path #
            if isinstance(value, basestring):
                value = track.load(value, readonly=True)
                tracks_to_close.append(value)
            if t.get('kind') == 'many':
                for i,_ in enumerate(value):
                    if isinstance(value[i], basestring):
                        value[i] = track.load(value[i], readonly=True)
                        tracks_to_close.append(value[i])
            # Add to the list of all tracks #
            if t.get('kind') == 'many': all_tracks += [x for x in value]
            else:                       all_tracks += [value]
            # Track collection must be combined #
            if t.get('kind') == 'many':
                value = TrackCollection(value, self.fields_collapse, self.chroms_collapse)
            # Variable fields case (track collection must collapse fields) #
            if t['fields'][-1] == '...':
                first_fields = t['fields'][:-1]
                rest_of_fields = [f for f in value.fields if f not in first_fields]
                value.fields = first_fields + rest_of_fields
            # Specific fields case #
            else: value.fields = t['fields']
            # What about track SimpleTrack case #
            pass #TODO
            # Add it to the dict #
            found_tracks[t['key']] = value
        # Check for generator case #
        if generator_call: return self.from_generator(found_tracks, found_args, args, kwargs)
        # Collapse chromosomes #
        if not self.chroms_collapse: chromosomes = all_tracks[0].chromosomes
        else: chromosomes = collapse(self.chroms_collapse, [t.chromosomes for t in all_tracks])
        # Multiple output tracks disabled #
        t = self.output_tracks[0]
        # Make a new virtual track #
        vtrack = VirtualTrack()
        # Output chromosome metadata #
        for chrom in chromosomes:
            vtrack.chrmeta[chrom] = {'length': max([i.chrmeta[chrom]['length'] for i in all_tracks])}
        # Output attributes #
        if t.get('datatype'): vtrack.datatype = t['datatype']
        # Output name #
        vtrack.name = self.long_name + ' on ' + andify_strings([i.name for i in all_tracks])
        ### Iterate on chromosomes ###
        for chrom in chromosomes:
            # Get special input arguments #
            for p in self.input_meta:
                if p['kind'] == 'chrom_len':
                    extra_args[p['key']] = vtrack.chrmeta[chrom]['length']
            # Call read on tracks #
            for k,input_track in found_tracks.items():
                if is_list(input_track): found_generators[k] = [i.read(chrom) for i in input_track]
                else:                    found_generators[k] = input_track.read(chrom)
            # What about track collapse and recursion #
            pass #TODO
            # Final argument list #
            final_args = {}
            for d in (found_args, found_generators, extra_args): final_args.update(d)
            # Call generate #
            data = self.generate(**final_args)
            # Variable fields case #
            if t['fields'][-1] == '...': fields = t['fields'][:-1] + rest_of_fields
            else:                        fields = t['fields']
            # Make a FeatureStream #
            stream = FeatureStream(data, fields)
            # Add it to the virtual track #
            vtrack.write(chrom, stream)
        # Close tracks later #
        vtrack.tracks_to_close = tracks_to_close
        # Add it #
        virtual_tracks.append(vtrack)
        # Return one virutal track or list of virtual tracks #
        return len(virtual_tracks) == 1 and virtual_tracks[0] or virtual_tracks

    def from_generator(self, found_generators, found_args, args, kwargs):
        """To be used when the manipulation is accessed
        directly with generators"""
        # Initialization #
        extra_args = {}
        # Parse special input arguments #
        for p in self.input_meta:
            if p['key'] in kwargs: value = kwargs[p['key']]
            elif len(args) >= p['position']: value = args[p['position']-1]
            elif p.get('default'): value = p['default']
            elif p.get('optional'): continue
            else: raise Exception("The special argument '%s' is missing for the generator '%s'." \
                                  % (p['kind'], self.short_name))
            # Cast it if it's not the right type #
            if not isinstance(value, p['type']): value = p['type'](value)
            # Add it to the dict #
            extra_args[p['key']] = value
        # Final argument list #
        final_args = {}
        for d in (found_args, found_generators, extra_args): final_args.update(d)
        return self.generate(**final_args)

################################################################################
# This module #
self_module = sys.modules[__name__]
# Where are the all the manipulations #
manips_directory = manips.__path__[0]
# A list containing their names #
list_of_manip_names = [name for loader, name, ispkg in pkgutil.iter_modules([manips_directory])]
# For every one make a callable function #
for manip_name in list_of_manip_names:
    manip_module = import_module('track.manips.' + manip_name)
    setattr(self_module, manip_name, Manipulation(manip_module))
# Add the documentation for every one #
self_module.__doc__ += '\n'.join(['.. autofunction:: %s' % s for s in list_of_manip_names])

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
