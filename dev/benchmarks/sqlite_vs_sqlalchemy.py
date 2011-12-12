"""
* sqlite3_via_index
0.158075094223
* sqlite3_via_names
0.196527004242
* sqlite3_via_slice
47.5213160515
* sqlalchemy_via_index1
0.392815113068
* sqlalchemy_via_index2
0.411301851273
* sqlalchemy_via_names1
2.35765194893
* sqlalchemy_via_names2
1.79039287567
* sqlalchemy_via_slice
0.47158408165
"""

import tempfile, sqlite3, os, random, string
from timeit import Timer
from collections import namedtuple
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select

################################################################################
def random_line_gen(start=1, step=5, nb_line=100, name_size=5, min=1, max=100):
    """
    Build a generator that will build a line like (start, stop, string, score).
    It simulates a minimal BED file.
    """
    random_name = lambda x: ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(x))
    for i in xrange(start, nb_line*step, step):
        yield i+start-1, i+start+step, random.uniform(min, max), random_name(name_size)

################################################################################
def build_random_db(table_name='table_name', delete_on_close=True):
    tmp_file = tempfile.NamedTemporaryFile(delete=delete_on_close)
    conn = sqlite3.connect(os.path.abspath(tmp_file.name))
    c = conn.cursor()
    c.execute('create table %s (start int, stop int, score real, name text)' % table_name)
    conn.commit()
    gen = random_line_gen(start=1, step=5, nb_line=500, name_size=5)
    c.executemany('insert into %s values (?, ?, ?, ?)' % table_name, gen)
    conn.commit()
    c.close()
    return tmp_file

################################################################################
def namedtuple_factory(cursor, row):
    fields = [col[0] for col in cursor.description]
    Row = namedtuple("Row", fields)
    return Row(*row)

################################################################################
def sqlite3_via_index(db, table_name='table_name'):
     conn = sqlite3.connect(os.path.abspath(db.name))
     c = conn.cursor()
     c.execute('select * from %s' % table_name)
     for row in c:
         start = row[0]
         stop = row[1]
         score = row[2]
         calc = start + stop + score

#---------------------------------------------------------------------------------#
def sqlite3_via_names(db, table_name='table_name'):
     conn = sqlite3.connect(os.path.abspath(db.name))
     conn.row_factory = sqlite3.Row
     c = conn.cursor()
     c.execute('select * from %s' % table_name)
     for row in c:
         start = row['start']
         stop = row['stop']
         score = row['score']
         calc = start + stop + score

#---------------------------------------------------------------------------------#
def sqlite3_via_slice(db, table_name='table_name'):
     conn = sqlite3.connect(os.path.abspath(db.name))
     conn.row_factory = namedtuple_factory
     c = conn.cursor()
     c.execute('select * from %s' % table_name)
     for row in c:
         calc = sum(row[0:2])

#---------------------------------------------------------------------------------#
def sqlalchemy_via_index1(engine):
    conn = engine.connect()
    result = conn.execute('select * from table_name')
    for row in result:
         start = row[0]
         stop = row[1]
         score = row[2]
         calc = start + stop + score

#---------------------------------------------------------------------------------#
def sqlalchemy_via_index2(engine, features):
    conn = engine.connect()
    sel = select([features])
    result = conn.execute(sel)
    for row in result:
         start = row[0]
         stop = row[1]
         score = row[2]
         calc = start + stop + score

#---------------------------------------------------------------------------------#
def sqlalchemy_via_names1(engine, features):
    conn = engine.connect()
    sel = select([features])
    result = conn.execute(sel)
    for row in result:
         start = features.c.name
         stop = features.c.stop
         score = features.c.score
         calc = start + stop + score

#---------------------------------------------------------------------------------#
def sqlalchemy_via_names2(session, features):
    features = session.query(Feature).all()
    for feat in features :
        start = feat.start
        stop = feat.stop
        score = feat.score
        calc = start + stop + score
    session.close()

#---------------------------------------------------------------------------------#
def sqlalchemy_via_slice(engine, features):
    conn = engine.connect()
    sel = select([features])
    result = conn.execute(sel)
    for row in result:
         calc = sum(row[0:2])

################################################################################
db = build_random_db()
engine = create_engine('sqlite:///%s'% os.path.abspath(db.name), echo=False)
#-----------------#
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()
#-----------------#
Base = declarative_base()
class Feature(Base):
    __tablename__ = 'table_name'
    start = Column(Integer, primary_key=True)
    stop = Column(Integer, primary_key=True)
    name = Column(String, primary_key=True)
    score = Column(Float)
#-----------------#
metadata = MetaData()
features = Table('table_name', metadata,
     Column('start', Integer, primary_key=True),
     Column('stop', String),
     Column('score', Float),
     Column('name', String))

################################################################################
nb_exec = 100

print '* sqlite3_via_index'
t = Timer("sqlite3_via_index(db)", "from __main__ import sqlite3_via_index, db")
print t.timeit(number=nb_exec)

print '* sqlite3_via_names'
t = Timer("sqlite3_via_names(db)", "from __main__ import sqlite3_via_names, db")
print t.timeit(number=nb_exec)

print '* sqlite3_via_slice'
t = Timer("sqlite3_via_slice(db)", "from __main__ import sqlite3_via_slice, db")
print t.timeit(number=nb_exec)

print '* sqlalchemy_via_index1'
t = Timer("sqlalchemy_via_index1(engine)", "from __main__ import sqlalchemy_via_index1, engine")
print t.timeit(number=nb_exec)

print '* sqlalchemy_via_index2'
t = Timer("sqlalchemy_via_index2(engine, features)", "from __main__ import sqlalchemy_via_index2, engine, features")
print t.timeit(number=nb_exec)

print '* sqlalchemy_via_names1'
t = Timer("sqlalchemy_via_names1(engine, features)", "from __main__ import sqlalchemy_via_names1, engine, features")
print t.timeit(number=nb_exec)

print '* sqlalchemy_via_names2'
t = Timer("sqlalchemy_via_names2(session, features)", "from __main__ import sqlalchemy_via_names2, session, features")
print t.timeit(number=nb_exec)

print '* sqlalchemy_via_slice'
t = Timer("sqlalchemy_via_slice(engine, features)", "from __main__ import sqlalchemy_via_slice, engine, features")
print t.timeit(number=nb_exec)

db.close()
