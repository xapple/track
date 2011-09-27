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

################
The Track object
################

.. autoclass:: Track

    .. automethod:: Track.read

    .. automethod:: Track.write

    .. automethod:: Track.remove

    .. automethod:: Track.rename

    .. automethod:: Track.save_as

    .. automethod:: Track.count

    .. automethod:: Track.ucsc_to_ensembl

    .. automethod:: Track.ensembl_to_ucsc

    .. automethod:: Track.score_vector

########
Comments
########
It is important to note that the general numbering convention of features on a chromosome varies depending on the source of the data. For instance, UCSC and Ensembl differ in this point such that an interval labeled `(start=4,end=8)` will span four base pairs according to UCSC but will span five base pairs according to Ensembl. The representation that the this packages sticks to is explained `here <http://bbcf.epfl.ch/twiki/bin/view/BBCF/NumberingConvention>`_.

A full `Developer documentation <http://bbcf.github.com/track/>`_ detailing all methods and classes is available.
