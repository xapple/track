===============================
Package *'track'* documentation
===============================

.. automodule:: track

###############
Loading a track
###############

.. autofunction:: load

####################
Creating a new track
####################

.. autofunction:: new

#################
Converting tracks
#################

.. autofunction:: convert

######################
Using the Track object
######################

.. autoclass:: Track

Track attributes
""""""""""""""""

.. autoattribute:: Track.fields
.. autoattribute:: Track.chromosomes
.. autoattribute:: Track.info
.. autoattribute:: Track.name
.. autoattribute:: Track.datatype
.. autoattribute:: Track.assembly
.. autoattribute:: Track.chrmeta
.. autoattribute:: Track.cursor

Track methods
"""""""""""""

.. automethod:: Track.read
.. automethod:: Track.write
.. automethod:: Track.save
.. automethod:: Track.rollback
.. automethod:: Track.close
.. automethod:: Track.export
.. automethod:: Track.remove
.. automethod:: Track.rename
.. automethod:: Track.count
.. automethod:: Track.guess_assembly
.. automethod:: Track.load_chr_file
.. automethod:: Track.export_chr_file
.. automethod:: Track.get_score_vector
.. automethod:: Track.ucsc_to_ensembl
.. automethod:: Track.ensembl_to_ucsc
.. automethod:: Track.roman_to_integer
.. automethod:: Track.integer_to_roman

###################
Loading into memory
###################

.. automodule:: track.memory
.. autofunction:: track.memory.read
.. autofunction:: track.memory.write

########
Comments
########
It is important to note that the general numbering convention of features on a chromosome varies depending on the source of the data. For instance, UCSC and Ensembl differ in this point such that an interval labeled `(start=4,end=8)` will span four base pairs according to UCSC but will span five base pairs according to Ensembl. The representation that the this packages sticks to is explained `here <http://bbcf.epfl.ch/twiki/bin/view/BBCF/NumberingConvention>`_.

##############
Reporting bugs
##############
Our `issue tracking system <https://github.com/bbcf/track/issues>`_  is found in the github repository. You are welcome to open a new ticket in it if you think you have found a bug. You will however need to create a github account if you don't already have one to open a new issue, sorry.

#######################
Developer documentation
#######################
A full `developer documentation <http://bbcf.github.com/track/>`_ detailing all methods and classes is available.
