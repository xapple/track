"""
Common stuff for python projects.
"""

########################### FILES FUNCTIONS ###################################
def iterate_lines(path, comment_char="#", linebreak_char="\\"):
    """
    Iterate over the lines of a text file in an intelligent way.
    1) Empty lines are skipped.
    2) Lines ending with line break characters such as '\\' are assembled.
    3) Lines starting with comments characters such as '#' are skipped.
    4) If the file is a GZIP, it is decompressed on the fly.
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
    if is_gzip(path):
        import gzip
        file = gzip.open(path, 'r')
        for line in lines(units(file)): yield line
        file.close()
    else:
        with open(path, 'r') as file:
            for line in lines(units(file)): yield line

#------------------------------------------------------------------------------#
def make_file_names(path):
    """
    Given a path to a file, generate more filenames.

    ::

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

#------------------------------------------------------------------------------#
def check_path(path):
    """
    Raise an exception if the path *path* is already taken.
    """
    import os
    if os.path.exists(path): raise Exception("The location '" + path + "' is already taken.")

#------------------------------------------------------------------------------#
def check_file(path):
    """
    Raise an exception if the path *path* is empty.
    """
    import os
    if os.path.getsize(path) == 0: raise Exception("The file '" + path + "' is empty.")

#------------------------------------------------------------------------------#
def check_executable(tool_name):
    """
    Raises an exception if the executable *tool_name* is not found.
    """
    import subprocess
    try:
        subprocess.Popen([tool_name], stderr=subprocess.PIPE)
    except OSError:
        raise Exception("The executable '" + tool_name + "' cannot be found")

#------------------------------------------------------------------------------#
def run_tool(tool_name, args):
    """
    Run the executable *tool_name* with *args* as arguments.
    Raises an exception if the process outputs something on the
    standard error output.
    """
    import subprocess
    proc = subprocess.Popen([tool_name] + args, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    if stderr: raise Exception("The tool '" + tool_name + "' exited with message: " + '"' + stderr.strip('\n') + '"')

#------------------------------------------------------------------------------#
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

#------------------------------------------------------------------------------#
def if_url_then_get_url(path):
    """
    If the path is an URL, download the file at that URL
    into a temporary file and return the path to that temporary
    file.
    If the path isn't an URL, return the path unchanged.
    """
    import os, urllib
    if path.startswith('http://') or path.startswith('https://'):
        extension = os.path.splitext(path)[1]
        tmp_path = temporary_path(extension)
        urllib.urlretrieve(path, tmp_path)
        return tmp_path
    else: return path

#------------------------------------------------------------------------------#
def is_gzip(path):
    """
    Returns true if the file at the given path is
    compressed using the gzip compression format.
    """
    with open(path, 'r') as file:
        if file.read(2) == '\x1f\x8b': return True
    return False

#------------------------------------------------------------------------------#
def load_dump(path, kind=None):
    if not kind:
        with open(path, 'r') as f: header = f.read(15)
        if header == 'SQLite format 3': kind = 'sql'
        else:                           kind = 'txt'
    if kind == 'txt':
        return open(path)
    if kind == 'sql':
        import sqlite3
        return sqlite3.connect(path).iterdump()

def assert_file_equal(pathA, pathB, start_a=0, start_b=0, end=999999, difflen=40, showlen=10):
    """
    Compare two file. If they are text they are simply loaded.
    If they are sqlite3 databases they are compared via their dumps
    Raise an exception if they are not equal, otherwise returns True.

    :param start_a: Start after these many lines from pathA.
    :param start_b: Start after these many lines from pathB.
    :param end: Stop after these many lines.
    :param difflen: Compute the difference on these many lines.
    :param showlen: Show these many lines from the difference.
    """
    # Load them #
    A, B = load_dump(pathA), load_dump(pathB)
    # Advance them #
    try:
        for x in xrange(start_a): A.next()
        for x in xrange(start_b): B.next()
    except StopIteration:
        pass
    # Compare them #
    import itertools
    for a,b,i in itertools.izip_longest(A,B,xrange(end)):
        if a != b:
            # They are different #
            import difflib
            diff = difflib.ndiff([a] + list(A)[0:difflen], [b] + list(B)[0:difflen])
            diff_text = '\n'.join(get_n_items_or_less(showlen, diff))
            # Raise and print differences #
            message = "The files:\n   %s'%s'%s and\n   %s'%s'%s differ.\n\n"
            message = message  % (Color.cyn, pathA, Color.end, Color.cyn, pathB, Color.end)
            message += "First %i lines of %i lines difference follows:\n"
            message = message  % (showlen, difflen)
            raise AssertionError(message + Color.wht + diff_text + Color.end)
    # They are identical #
    return True

#------------------------------------------------------------------------------#
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

#------------------------------------------------------------------------------#
def empty_file(path):
    """
    Create an empty file at the path specified.
    """
    with open(path, 'w') as f: pass

########################## ITERATOR FUNCTIONS ##################################
def sentinelize(iterable, sentinel):
    """
    Add an item to the end of an iterable.

    ::

        >>> list(sentinelize(range(4), 99))
        [0, 1, 2, 3, 99]
    """
    for item in iterable: yield item
    yield sentinel

#------------------------------------------------------------------------------#
def get_next_item(iterable):
    """
    Gets the next item of an iterable.
    If the iteratable is exhausted, returns None.

    ::

        >>> get_next_item(iter(range(4)))
        0
        >>> get_next_item(iter([]))
    """
    try:
        x = iterable.next()
    except StopIteration:
        x = None
    except AttributeError:
        x = None
    return x

#------------------------------------------------------------------------------#
def get_n_items_or_less(n, iterable):
    """
    Gets the n next items of an iterable or less
    if the iterator is exhausted before

    ::

        >>> get_n_items_or_less(6, iter(range(10)))
        [0, 1, 2, 3, 4, 5]
        >>> get_n_items_or_less(6, iter(range(4)))
        [0, 1, 2, 3]
    """
    result = []
    try:
        for i in xrange(n):
            result.append(iterable.next())
    except StopIteration:
        pass
    return result

#------------------------------------------------------------------------------#
def pick_iterator_elements(iterable, indices):
    """
    Return a new iterator, yielding only those elements
    of the original iterator.

    ::

        >>> list(pick_iterator_elements(iter([('a','b','c'),(10,20,30)]), (0,2)))
        [['a', 'c'], [10, 30]]
    """
    for item in iterable: yield [item[i] for i in indices]

############################## VARIOUS FUNCTIONS ###############################
def format_float(f, precision=None):
    """
    Formats a float, by rounding it and striping unnecesarry zeros.
    But it always leaves one zero after the decimal point.

    ::

        >>> format_float(0.100)
        '0.1'
        >>> format_float(0.1001)
        '0.1001'
        >>> format_float(0.10000001)
        '0.1'
        >>> format_float(101.0)
        '101.0'
        >>> format_float(100001.1)
        '100000.0'
        >>> format_float(1000.0/6.0)
        '166.7'
        >>> format_float(999.9)
        '999.9'
        >>> format_float(999.99)
        '1000.0'
    """
    if precision: return '%s' % float('%.'+str(precision)+'g' % f)
    else:         return '%s' % float('%.4g' % f)

#------------------------------------------------------------------------------#
def natural_sort(item):
    """
    Sort strings that contain numbers correctly.

    ::

        >>> l = ['v1.3.12', 'v1.3.3', 'v1.2.5', 'v1.2.15', 'v1.2.3', 'v1.2.1']
        >>> l.sort(key=natural_sort)
        >>> l.__repr__()
        "['v1.2.1', 'v1.2.3', 'v1.2.5', 'v1.2.15', 'v1.3.3', 'v1.3.12']"
    """
    if item is None: return 0
    import re
    def try_int(s):
        try: return int(s)
        except ValueError: return s
    return map(try_int, re.findall(r'(\d+|\D+)', item))

###############################################################################
def collapse(method, collection):
    """
    Collapse lists in specific ways.

    :param method: the method used to collapse. Can be one of: ``adding``, ``appending``, ``union`` or ``intersection``,
    :type method: string
    :param collection: a list of things
    :type collection: list
    :returns: a new list

    >>> collapse('adding',[1,5,2])
    8
    >>> collapse('adding',[3])
    3
    >>> collapse('appending',[[1,5],[5,3],[2,1]])
    [1, 5, 5, 3, 2, 1]
    >>> collapse('appending',[[1,2,3]])
    [1, 2, 3]
    >>> collapse('union',[[1,5],[5,3],[2,1]])
    [1, 5, 3, 2]
    >>> collapse('intersection',[[1,5,4],[5,3,3],[2,6,5]])
    [5]
    >>> collapse('intersection',[['a', 'b', 'c', 'd'], ['a', 'b', 'c', 'd', 'e', 'f']])
    ['a', 'b', 'c', 'd']
    >>> collapse('first',[[1,5,4],[5,3,3],[2,6,5]])
    [1, 5, 4]
    >>> collapse('last',[[1,5,4],[5,3,3],[2,6,5]])
    [2, 6, 5]
    """
    if method == 'adding':
        return sum(collection)
    elif method == 'appending':
        return [x for y in collection for x in y]
    elif method == 'union':
        seen = set()
        return [x for y in collection for x in y if x not in seen and not seen.add(x)]
    elif method == 'intersection':
        common_items = reduce(set.intersection, map(set,collection))
        return [i for i in collection[0] if i in common_items]
    elif method == 'first':
        return collection[0]
    elif method == 'last':
        return collection[-1]

#------------------------------------------------------------------------------#
def int_to_roman(input):
    """
    Convert an integer to a roman numeral.

    ::

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

#------------------------------------------------------------------------------#
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

#------------------------------------------------------------------------------#
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

############################## CLASSES #########################################
class Color:
    """Shortcuts for the ANSI escape sequences to control
       formatting, color, etc. on text terminals. Use it like this::

            print Color.red + "Hello world" + Color.end
    """
    # Special #
    end = '\033[0m'
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
    # Light #
    light = '\033[2m'
    l_blk = '\033[2;30m' # Black
    l_red = '\033[2;31m' # Red
    l_grn = '\033[2;32m' # Green
    l_ylw = '\033[2;33m' # Yellow
    l_blu = '\033[2;34m' # Blue
    l_pur = '\033[2;35m' # Purple
    l_cyn = '\033[2;36m' # Cyan
    l_wht = '\033[2;37m' # White
    # Italic #
    italic = '\033[1m'
    i_blk = '\033[3;30m' # Black
    i_red = '\033[3;31m' # Red
    i_grn = '\033[3;32m' # Green
    i_ylw = '\033[3;33m' # Yellow
    i_blu = '\033[3;34m' # Blue
    i_pur = '\033[3;35m' # Purple
    i_cyn = '\033[3;36m' # Cyan
    i_wht = '\033[3;37m' # White
    # Underline #
    underline = '\033[4m'
    u_blk = '\033[4;30m' # Black
    u_red = '\033[4;31m' # Red
    u_grn = '\033[4;32m' # Green
    u_ylw = '\033[4;33m' # Yellow
    u_blu = '\033[4;34m' # Blue
    u_pur = '\033[4;35m' # Purple
    u_cyn = '\033[4;36m' # Cyan
    u_wht = '\033[4;37m' # White
    # Glitter #
    flash = '\033[5m'
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

#------------------------------------------------------------------------------#
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

    def save(self):
        self.modified = False
        self.backup = self.data.copy()

    def rollback(self):
        self.modified = False
        self.data = self.backup.copy()

    def overwrite(self, d):
        self.modified = True
        self.data = d

#------------------------------------------------------------------------------#
class Timer:
    """Times a given code block. Use it like this:

            with Timer('my batch process'): batch_benchmark(args)

    """

    def __init__(self, name=None, entries=1):
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
        line1 = "%.6f seconds for %s" % (total_time, self.name or 'Unnamed')
        line2 = "(%.3f usec per entry)" % entry_time
        print line1, line2

############################## DECORATORS #####################################
def property_cached(f):
    """Decorator for properties evaluated only once.
    It can be used to created a cached property like this::

        class Employee(object):
            @property_cached
            def salary(self):
                return 8000

        bob = Employee()
        print bob.salary
    """
    def get_method(self):
        try:
            return self.__cache__[f]
        except AttributeError:
            self.__cache__ = {}
            x = self.__cache__[f] = f(self)
            return x
        except KeyError:
            x = self.__cache__[f] = f(self)
            return x
    get_method.__doc__ = f.__doc__
    return property(get_method)
