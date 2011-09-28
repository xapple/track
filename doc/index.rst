=============================
Package 'track' documentation
=============================

.. automodule:: track

###############
Loading a track
###############

.. autofunction:: load

####################
Creating a new track
####################

.. autofunction:: new

##################
Converting formats
##################

.. autofunction:: convert

######################
Using the Track object
######################

.. autoclass:: Track

    .. automethod:: Track.save

    .. automethod:: Track.rollback

    .. automethod:: Track.close

    .. automethod:: Track.export

    .. automethod:: Track.read

    .. automethod:: Track.write

    .. automethod:: Track.remove

    .. automethod:: Track.rename

    .. automethod:: Track.count

    .. automethod:: Track.get_score_vector

    .. automethod:: Track.ucsc_to_ensembl

    .. automethod:: Track.ensembl_to_ucsc

    .. automethod:: Track.roman_to_integer

    .. automethod:: Track.integer_to_roman

###################
Loading into memory
###################

.. automodule:: track.memory

    .. autofunction:: read

    .. autofunction:: write

########
Comments
########
It is important to note that the general numbering convention of features on a chromosome varies depending on the source of the data. For instance, UCSC and Ensembl differ in this point such that an interval labeled `(start=4,end=8)` will span four base pairs according to UCSC but will span five base pairs according to Ensembl. The representation that the this packages sticks to is explained `here <http://bbcf.epfl.ch/twiki/bin/view/BBCF/NumberingConvention>`_.

#######################
Developer documentation
#######################
A full `developer documentation <http://xapple.github.com/track/>`_ detailing all methods and classes is available.
