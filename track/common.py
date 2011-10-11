"""
Common stuff for python projects.
"""

###############################################################################
def iterate_lines(path, comment_char="#", linebreak_char=r"\\"):
    """
    Iterate over the lines of a text file in an intelligent way.
    1) Empty lines are skipped.
    3) Lines starting with comments characters such as '#' are skipped.
    2) Lines ending with line break characters such as '\\' are assembled.
    This function yields the line number and the line content as a tuple.
    """
    # The pieces of a file are every block of data separated by the newline character.
    # The units of the file are composed by taking the pieces and removing empty and comment lines.
    # The actual lines of the file are composed by taking the units and joining line breaks.
    def units(iterable):
        for number, piece in enumerate(iterable):
            piece = piece.strip()
            if len(piece) == 0: continue
            if piece.startswith(comment_char): continue
            yield number, piece
    def lines(iterable):
        for number, unit in iterable:
            while unit.endswith(linebreak_char):
                unit = unit.strip(linebreak_char)
                unit += iterable.next()[1]
            yield number, unit
    with open(path, 'r') as file:
        for line in lines(units(file)): yield line

################################################################################
def make_file_names(path):
    """
    Given a path to a file, generate more filenames.

    >>> g = make_file_names("tmp/test.png")
    >>> g.next()
    'tmp/test.png'
    >>> g.next()
    'tmp/test_1.png'
    >>> g.next()
    'tmp/test_2.png'
    """
    yield path
    import sys, os
    constant, ext = os.path.splitext(path)
    for i in xrange(1,sys.maxint): yield constant + "_" + str(i) + ext

################################################################################
def check_path(path):
    """
    Raise an exception if the path *path* is already taken.
    """
    import os
    if os.path.exists(path): raise Exception("The location '" + path + "' is already taken")

################################################################################
def check_executable(tool_name):
    """
    Raises an exception if the executable *tool_name* is not found.
    """
    import subprocess
    try:
        subprocess.Popen([tool_name], stderr=subprocess.PIPE)
    except OSError:
        raise Exception("The executable '" + tool_name + "' cannot be found")

################################################################################
def natural_sort(item):
    """
    Sort strings that contain numbers correctly.

    >>> l = ['v1.3.12', 'v1.3.3', 'v1.2.5', 'v1.2.15', 'v1.2.3', 'v1.2.1']
    >>> l.sort(key=natural_sort)
    >>> l.__repr__()
    "['v1.2.1', 'v1.2.3', 'v1.2.5', 'v1.2.15', 'v1.3.3', 'v1.3.12']"
    """
    import re
    def try_int(s):
        try: return int(s)
        except ValueError: return s
    return map(try_int, re.findall(r'(\d+|\D+)', item))

################################################################################
def temporary_path(suffix=''):
    """
    Often, one needs a new random and temporary file path
    instead of the random and temporary file object provided
    by the 'tempfile' module.
    """
    import tempfile
    file = tempfile.NamedTemporaryFile(suffix=suffix)
    path = file.name
    file.close()
    return path

################################################################################
def sentinelize(iterable, sentinel):
    """
    Add an item to the end of an iterable.

    >>> list(sentinelize(range(4), 99))
    [0, 1, 2, 3, 99]
    """
    for item in iterable: yield item
    yield sentinel

################################################################################
def pick_iterator_elements(iterable, indices):
    """
    Return a new iterator, yielding only those elements
    of the original iterator.

    >>> list(pick_iterator_elements(iter([('a','b','c'),(10,20,30)]), (0,2)))
    [('a','c'), (10,30)]
    """
    for item in iterable: yield [item[i] for i in indices]

################################################################################
def assert_sql_equal(file_a, file_b):
    """
    Compare two two sqlite3 databases via their dumps.
    Raise an exception if they are not equal, otherwise
    return True.
    """
    import itertools, sqlite3
    A = sqlite3.connect(file_a)
    B = sqlite3.connect(file_b)
    for a,b in itertools.izip_longest(A.iterdump(), B.iterdump()):
        if a != b:
            intro  = Colors.ylw + "First difference in dump follows" + Colors.end
            A_line = Colors.b_ylw + "A: " + Colors.end + a
            B_line = Colors.b_ylw + "B: " + Colors.end + b
            raise AssertionError(intro + "\n" + A_line + "\n" + B_line)
    return True

################################################################################
def empty_sql_file(path):
    """
    Create an empty sql file at the path specified.
    """
    import sqlite3
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    connection.commit()
    cursor.close()
    connection.close()

################################################################################
def empty_file(path):
    """
    Create an empty file at the path specified.
    """
    with open(path, 'w') as f: pass

################################################################################
def int_to_roman(input):
    """
    Convert an integer to a roman numeral.

    >>> int_to_roman(1999)
    'MCMXCIX'
    """
    ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
    nums = ('M',  'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
    if type(input) != type(1): raise TypeError, 'Expected integer, got "%s."' % type(input)
    if not 0 < input < 4000: raise ValueError, 'Argument must be between 1 and 3999.'
    result = ""
    for i in range(len(ints)):
       count   = int(input / ints[i])
       result += nums[i] * count
       input  -= ints[i] * count
    return result

################################################################################
def roman_to_int(input):
    """
    Convert a roman numeral to an integer.

    >>> orig_integers = range(1, 4000)
    >>> romans = [int_to_roman(i) for i in orig_integers]
    >>> computed_integers = [roman_to_int(r) for r in romans]
    >>> print orig_integers == computed_integers
    True
    """
    ints = [1000, 500, 100, 50,  10,  5,   1]
    nums = ['M', 'D', 'C', 'L', 'X', 'V', 'I']
    if type(input) != type(""): raise TypeError, 'Expected string, got "%s."' % type(input)
    input = input.upper()
    places = []
    for c in input:
        if not c in nums:
            raise ValueError, 'Input is not a valid roman numeral: "%s."' % input
    for i in range(len(input)):
        c = input[i]
        value = ints[nums.index(c)]
        try:
            nextvalue = ints[nums.index(input[i +1])]
            if nextvalue > value: value *= -1
        except IndexError: pass
        places.append(value)
    output = sum([n for n in places])
    if int_to_roman(output) == input: return output
    else: raise ValueError, 'Input is not a valid roman numeral: "%s."' % input

################################################################################
class Colors:
    """Shortcuts for the ANSI escape sequences to control
       formatting, color, etc. on text terminals. Use it like this:

        print Colors.red + "Hello world" + Colors.end

    """
    # Special #
    end =  '\033[0m'
    underline = '\033[4m'
    # Regular #
    blk   = '\033[0;30m' # Black
    red   = '\033[0;31m' # Red
    grn   = '\033[0;32m' # Green
    ylw   = '\033[0;33m' # Yellow
    blu   = '\033[0;34m' # Blue
    pur   = '\033[0;35m' # Purple
    cyn   = '\033[0;36m' # Cyan
    wht   = '\033[0;37m' # White
    # Bold #
    bold  = '\033[1m'
    b_blk = '\033[1;30m' # Black
    b_red = '\033[1;31m' # Red
    b_grn = '\033[1;32m' # Green
    b_ylw = '\033[1;33m' # Yellow
    b_blu = '\033[1;34m' # Blue
    b_pur = '\033[1;35m' # Purple
    b_cyn = '\033[1;36m' # Cyan
    b_wht = '\033[1;37m' # White
    # Underline #
    u_blk = '\033[4;30m' # Black
    u_red = '\033[4;31m' # Red
    u_grn = '\033[4;32m' # Green
    u_ylw = '\033[4;33m' # Yellow
    u_blu = '\033[4;34m' # Blue
    u_pur = '\033[4;35m' # Purple
    u_cyn = '\033[4;36m' # Cyan
    u_wht = '\033[4;37m' # White
    # Glitter #
    g_blk = '\033[5;30m' # Black
    g_red = '\033[5;31m' # Red
    g_grn = '\033[5;32m' # Green
    g_ylw = '\033[5;33m' # Yellow
    g_blu = '\033[5;34m' # Blue
    g_pur = '\033[5;35m' # Purple
    g_cyn = '\033[5;36m' # Cyan
    g_wht = '\033[5;37m' # White
    # Fill #
    f_blk = '\033[40m'   # Black
    f_red = '\033[41m'   # Red
    f_grn = '\033[42m'   # Green
    f_ylw = '\033[43m'   # Yellow
    f_blu = '\033[44m'   # Blue
    f_pur = '\033[45m'   # Purple
    f_cyn = '\033[46m'   # Cyan
    f_wht = '\033[47m'   # White

################################################################################
class JournaledDict(object):
    """
    A dictionary like object that tracks modification to itself.
    It has an extra special boolean self.modified value that starts off with "False"
    It has three special methods: self.save(), self.rollback() and self.overwrite()

       * rollback() will reset the self.modified variable to False and restore
    the dictionary to it's previous state.

       * save()  will reset the self.modified variable to False and remember
    the dictionary current's state.

       * overwrite(d) will reset the self.modified variable to True and repalce
    the dictionary with the one passed to it.
    """

    def __init__(self, d=None):
        # The dictionary itself #
        if d: self.data = d
        else: self.data = {}
        # The remembered state #
        self.backup = self.data.copy()
        # The boolean value #
        self.modified = False

    def __cmp__(self, d):
        if isinstance(d, JournaledDict): return cmp(self.data, d.data)
        else: return cmp(self.data, d)

    def __getitem__(self, key):
        if key in self.data: return self.data[key]
        if hasattr(self.__class__, "__missing__"): return getattr(self.__class__, "__missing__")(self, key)
        raise KeyError(key)

    def __setitem__(self, key, item):
        self.modified = True
        self.data[key] = item

    def __delitem__(self, key):
        self.modified = True
        del self.data[key]

    def __repr__(self): return repr(self.data)
    def __iter__(self): return iter(self.data)
    def __contains__(self, key): return key in self.data
    def __len__(self): return len(self.data)
    def keys(self): return self.data.keys()
    def items(self): return self.data.items()
    def iteritems(self): return self.data.iteritems()
    def iterkeys(self): return self.data.iterkeys()
    def itervalues(self): return self.data.itervalues()
    def values(self): return self.data.values()
    def has_key(self, key): return key in self.data
    def get(self, key, d=None): return self.data.get(key, d)

    #-----------------------------------------------------------------------------#
    def clear(self):
        self.modified = True
        self.data.clear()

    def setdefault(self, key, failobj=None):
        if key not in self:
            self.modified = True
            self[key] = failobj
        return self[key]

    def pop(self, key, *args):
        self.modified = True
        return self.data.pop(key, *args)

    def popitem(self):
        self.modified = True
        return self.data.popitem()

    def copy(self):
        return JournaledDict(self.data.copy())

    def update(self, d=None, **kwargs):
        if d is None: return
        self.modified = True
        if isinstance(d, JournaledDict): self.data.update(d.data)
        elif isinstance(d, dict) or not hasattr(d, 'items'): self.data.update(d)
        else:
            for k, v in d.items(): self[k] = v
        if len(kwargs): self.data.update(kwargs)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable: d[key] = value
        return d

    #-----------------------------------------------------------------------------#

    def save(self):
        self.modified = False
        self.backup = self.data.copy()

    def rollback(self):
        self.modified = False
        self.data = self.backup.copy()

    def overwrite(self, d):
        self.modified = True
        self.data = d

################################################################################
class JsonJit(object):
    """
    JsonJit is a class for Just In Time instantiation of JSON resources.
    The __lazy__ method downloads the JSON resource from the server.
    But the __lazy__ method is called only when the first attribute is either get or set.
    You can use it like this:

        assemblies = JsonJit('http://bbcftools.vital-it.ch/genrep/assemblies.json', 'assembly')

    :param url: Location of the JSON to load
    :param list_key: Optional dictionary key to unpack the elements of JSON with
    """

    def __init__(self, url, list_key=None):
        """Save the passed parameters"""
        self.__dict__['url'] = url
        self.__dict__['list_key'] = list_key
        self.__dict__['obj'] = None

    def __lazy__(self):
        """Fetch resource and instantiate object."""
        import json, urllib2
        try:
            content = urllib2.urlopen(self.url).read()
            # Create the child object #
            self.__dict__['obj'] = json.loads(content)
        except urllib2.URLError as err:
            self.__dict__['obj'] = err
        # Unpack the child object #
        if self.list_key:
            for num, item in enumerate(self.obj):
                self.obj[num] = item[self.list_key]

    def get(self, value):
        """Retrieve an item from the JSON
           by searching all attributes of all items
           for *name*"""
        if not self.obj: self.__lazy__()
        for x in self.obj:
            if [k for k,v in x.items() if v == value]: return x

    def filter(self, key, value):
        """Retrieve an item from the JSON
           by search a key that is equal to value in
           all elements"""
        if not self.obj: self.__lazy__()
        return [x for x in self.obj for k,v in x.items() if v == value and k == key]

    def by(self, name):
        """Return a list of attributes present
           in every element of the JSON"""
        if not self.obj: self.__lazy__()
        return [x.get(name).encode('ascii') for x in self.obj]

    def make(self, name):
        """Return an object whoes attributes are the
           keys of the element's dictionary"""
        if not self.obj: self.__lazy__()
        class JsonObject(object): pass
        obj = JsonObject()
        obj.__dict__.update(self.get(name))
        return obj

    def __getattr__(self, name):
        """Method called when an attribute is
           not found in __dict__."""
        if not self.obj: self.__lazy__()
        # Search in the child object #
        try: return getattr(self.obj, name)
        except AttributeError as err:
            # Search in the parent object #
            if name in self.__dict__: return self.__dict__[name]
            else: return self.make(name)

    def __setattr__(self, name, value):
        """Method called when an attribute is
           assigned to."""
        if not self.obj: self.__lazy__()
        try: setattr(self.obj, name, value)
        except AttributeError:
            self.__dict__[name] = value

    def __len__(self):
        if not self.obj: self.__lazy__()
        return self.obj.__len__()

    def __iter__(self):
        if not self.obj: self.__lazy__()
        return self.obj.__iter__()

    def __repr__(self):
        if not self.obj: self.__lazy__()
        return self.obj.__repr__()

    def __getitem__(self, key):
        if not self.obj: self.__lazy__()
        return self.obj[key]

    def __setitem__(self, key, item):
        if not self.obj: self.__lazy__()
        self.obj[key] = item

    def __delitem__(self, key):
        if not self.obj: self.__lazy__()
        del self.obj[key]

################################################################################
class Timer:
    """Times a given code block. Use it like this:

            with Timer('my batch process'): batch_benchmark(args)

    """

    def __init__(self, name, entries):
        import timeit
        self.name = name
        self.entries = entries
        self.timer = timeit.default_timer

    def __enter__(self):
        self.start = self.timer()
        return self

    def __exit__(self, *args):
        self.end = self.timer()
        total_time = self.end - self.start
        entry_time = (1000000*total_time / self.entries)
        line1 = "%.6f seconds for " % total_time + self.name
        line2 = "(%.3f usec per entry)" % entry_time
        print line1, line2

################################################################################
def profile_it(command):
    """Profiles a given command and returns a pstat object.
       Use it like this:

            r = profile_it('batch_benchmark(args)')
            r.sort_stats('time', 'cum')
            r.print_stats(10)

    """
    import os, cProfile, pstats
    result_file = temporary_path('.profile')
    cProfile.run(command, result_file)
    results = pstats.Stats(result_file)
    results.sort_stats('time', 'cum')
    results.print_stats(20)
    os.remove(result_file)
    return results
