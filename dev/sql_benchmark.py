# Modules #
import sqlite3
from inspect import getfile, currentframe
from functools import partial
import os, timeit, random, tempfile

# Variables #
global num_entries
num_entries = 1000000

###############################################################################
# General Functions #
def setup_database(db_path, auto_commit=None):
    global connection, cursor
    if auto_commit: connection = sqlite3.connect(db_path, isolation_level=None) # commit all the time
    else:           connection = sqlite3.connect(db_path)                       # no commits ever (default)
    cursor = connection.cursor()
    cursor.execute('create table dummy (one text, two text, three integer)')
    connection.commit()

def destroy_database(db_path):
    os.remove(db_path)

def reopen_database(db_path):
    global connection, cursor
    cursor.close()
    connection.close()
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

def generate_data():
    global num_entries
    name_gen = tempfile._RandomNameSequence()
    for i in range(num_entries):
        yield (name_gen.next(), name_gen.next(), random.randint(1,1000))

def time_the_execution(command):
    global num_entries
    timeit_count = 1
    t = timeit.Timer(command)
    sec = t.timeit(timeit_count)
    string = "%.6f sec for " % sec + command.func.__name__
    print string.ljust(40) + "(%.3f usec per entry)" % (1000000*sec / num_entries)

###############################################################################
# Write Fonctions #
def simple_execute(iterable):
    global connection, cursor
    for x in iterable:
        cursor.execute('insert into dummy values (?,?,?)', x)
    cursor.close()
    connection.commit()
    connection.close()

def batch_execute(iterable):
    global connection, cursor
    cursor.executemany('insert into dummy values (?,?,?)', iterable)
    cursor.close()
    connection.commit()
    connection.close()

def simple_variable_table(iterable):
    global connection, cursor
    table = 'dummy'
    for x in iterable:
        cursor.execute('insert into ' + table + ' values (?,?,?)', x)
    cursor.close()
    connection.commit()
    connection.close()

def batch_variable_table(iterable):
    global connection, cursor
    table = 'dummy'
    cursor.executemany('insert into ' + table + ' values (?,?,?)', iterable)
    cursor.close()
    connection.commit()
    connection.close()

def variable_fields(iterable):
    global connection, cursor
    fields = ['one','two','three']
    table = 'dummy'
    cursor.executemany('insert into ' + table + ' values (' + ','.join(['?' for x in range(len(fields))]) + ')', iterable)
    cursor.close()
    connection.commit()
    connection.close()

def bad_bad_execute(iterable):
    # Don't do this
    global connection, cursor
    for x in iterable:
        cursor.execute('insert into dummy values ("' +x[0]+ '","' +x[1]+ '",' +str(x[2])+ ')')
    cursor.close()
    connection.commit()
    connection.close()

###############################################################################
# Read functions #
def read_one_by_one(command):
    cursor.execute(command)
    sum = 0
    while True:
        try:
            x = cursor.fetchone()
            sum += x[2]
        except TypeError as err:
            break

def read_all(command):
    cursor.execute(command)
    sum = 0
    data = cursor.fetchall()
    data = list(data)
    for x in data:
        sum += x[2]

def read_iterator(command):
    cursor.execute(command)
    sum([x[2] for x in cursor])

###############################################################################
# Write #
if __name__=='__main__':
    this_dir = '/'.join(os.path.abspath(getfile(currentframe())).split('/')[:-1])+'/'
    db_path = this_dir + "test_database.sql"

    data = list(generate_data())

    print "--write--"
    setup_database(db_path)
    time_the_execution(partial(simple_execute, data))
    destroy_database(db_path)

    setup_database(db_path)
    time_the_execution(partial(batch_execute, data))
    destroy_database(db_path)

    setup_database(db_path)
    time_the_execution(partial(simple_variable_table, data))
    destroy_database(db_path)

    setup_database(db_path)
    time_the_execution(partial(batch_variable_table, data))
    destroy_database(db_path)

    setup_database(db_path)
    time_the_execution(partial(variable_fields, data))
    destroy_database(db_path)

    setup_database(db_path)
    time_the_execution(partial(bad_bad_execute, data))

###############################################################################
# Read #
    print "--read--"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    command = "select * from dummy"

    reopen_database(db_path)
    time_the_execution(partial(read_one_by_one, command))

    reopen_database(db_path)
    time_the_execution(partial(read_all, command))

    reopen_database(db_path)
    time_the_execution(partial(read_iterator, command))


###############################################################################
    cursor.close()
    connection.close()
    destroy_database(db_path)
