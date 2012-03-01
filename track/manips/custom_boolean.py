# coding: utf-8

################################### Modules ####################################
import sys
import types
from track import common

################################# Description ##################################
label           = 'custom_boolean'
short_name      = 'Custom boolean'
long_name       = 'Execute a custom boolean'
input_tracks    = [{'key':'n_tracks', 'position':1, 'kind':'many',
                    'fields':['start','end','name','score','strand']}]
input_args      = [{'key':'fn', 'position':2, 'type':types.FunctionType,
                    'doc':'A function that takes a vector and returns a boolean.'},
                   {'key':'win_size', 'position':3, 'type': int, 'default': 1000,
                    'doc':'The number of basepairs loaded in memory at each iteration (default: 1000).'}]
input_meta      = []
output_tracks   = [{'position':1, 'fields': ['start','end']}]
tracks_collapse = None
fields_collapse = None
chroms_collapse = 'union'

################################ Documentation #################################
tooltip = \
"""
The ``custom_boolean`` manipulation takes several tracks *t_1*,..,*t_n* and a
boolean function *fn* as input, and returns one track that is *fn(t_1,..,t_n)*.
The window size *win_size* determines how many basepairs of each track are
loaded in memory at a time (default: 1000).
"""

tickets = []

################################## Examples ####################################
numeric_example = \
"""
X1 [start,end]: [(4,5),(7,9),(10,12)]
X2 [start,end]: [(1,3),(4,5),(11,14)]
X3 [start,end]: [(9,13)]
fn: not(X1) and (X2 or X3)
R               [(1,3),(9,10),(12,14)]
"""

visual_example = \
u"""
X1: ───▤▤▤▤▤▤▤▤─────────────────────
X2: ─▤▤▤▤▤▤─────────────────────────
X3: ─────▤▤▤▤▤▤▤▤▤──────────────────
fn: X1 and X2 and X3
R:  ─────▤▤─────────────────────────
"""

#################################### Tests #####################################
def test_bool_fn(b):
    return not(b[0]) and (b[1] or b[2])

def fill(l):
    return [(x[0],x[1],'',0.0,0) for x in l]

tests = [
    # Test AND
    {'tracks':   {'n_tracks': [iter(fill([(4,5),(7,9),(8,9),(10,12),(14,16),(21,28)])),
                               iter(fill([(1,3),(4,5),(11,14),(15,18),(19,20)])),
                               iter(fill([(9,13),(14,19),(22,25),(32,34)]))] },
     'args':     {'fn': lambda x: all(x), 'win_size':10},
     'chromosome': 'chrI',
     'expected': fill([(11,12),(15,16)])},

    # Test OR
    {'tracks':   {'n_tracks': [iter(fill([(4,5),(7,9),(10,12)])),
                               iter(fill([(1,3),(4,5),(11,14)])),
                               iter(fill([(9,13)]))] },
     'args':     {'fn': lambda x: any(x)},
     'chromosome': 'chrI',
     'expected': fill([(1,3),(4,5),(7,14)])},

    # Test custom fct
    {'tracks':   {'n_tracks': [iter(fill([(4,5),(7,9),(10,12)])),
                               iter(fill([(1,3),(4,5),(11,14)])),
                               iter(fill([(9,13)]))] },
     'args':     {'fn': test_bool_fn, 'win_size': 5},
     'chromosome': 'chrI',
     'expected': fill([(1,3),(9,10),(12,14)])}]

############################### Implementation #################################
def generate(**kwargs):
    from gMiner.manipulate import fusion
    for f in fusion(meta_generate(**kwargs)): yield f

def meta_generate(n_tracks, fn, win_size):
    from gMiner.manipulate import fusion
    tracks = n_tracks
    sentinel = (sys.maxint, sys.maxint, 0.0)
    tracks = [fusion(t) for t in tracks]
    tracks = [common.sentinelize(t, sentinel) for t in tracks]

    N = len(tracks)
    init = [tracks[i].next() for i in range(N)]
    for i in xrange(N-1,-1,-1):
        if init[i] == sentinel: # empty track
            N-=1
            tracks.pop(i)
            init.pop(i)
    available_tracks = range(N-1,-1,-1)
    activity = [False]*N
    current = []
    current.extend([(init[i][0],i) for i in range(N)])
    current.extend([(init[i][1],i) for i in range(N)])
    current.sort()

    start = current[0][0]
    while current[0][0] == start:
        activity[current[0][1]] = True
        z = current.pop(0)

    k=1
    while available_tracks:
        # load *win_size* bp in memory
        to_remove = []
        for i in available_tracks:
            a = [0,0]
            limit = k*win_size
            while a[1] < limit:
                a = tracks[i].next()
                if a == sentinel:
                    to_remove.append(i)
                    break
                current.append((a[0],i))
                current.append((a[1],i))
        for i in to_remove:
            available_tracks.remove(i)
        current.sort()

        # calculate boolean values for start-next interval
        while current and current[0][0] < limit:
            next = current[0][0]
            res = fn(activity)
            if res:
                yield (start,next,'',0.0,0)
            while current and current[0][0] == next:
                i = current[0][1]
                activity[i] = not(activity[i])
                z = current.pop(0)
            start = next
        k+=1

