===============================
Package *'track'* documentation
===============================

Provides easy read/write access to genomic tracks in a fashion that is independent from the underlying format. Requires Python 2.6 or higher.
Currently the following formats are implemented:

* `BioSQLite <http://bbcf.epfl.ch/twiki/bin/view/BBCF/SqLite>`_, `BED <http://genome.ucsc.edu/FAQ/FAQformat.html#format1>`_, `WIG <http://genome.ucsc.edu/goldenPath/help/wiggle.html>`_, `GFF <http://genome.ucsc.edu/FAQ/FAQformat.html#format3>`_, `GTF <http://genome.ucsc.edu/FAQ/FAQformat.html#format4>`_, `bedGraph <http://genome.ucsc.edu/goldenPath/help/bedgraph.html>`_, `bigWig <http://genome.ucsc.edu/goldenPath/help/bigWig.html>`_

More formats can be added easily.

=======
Example
=======

To get access to the information contained inside an already existing genomic track, you would do the following whatever the format of the track is::

    import track
    with track.load('tracks/rp_genes.bed') as rp:
        data = rp.read('chr3')

=================
Table of contents
=================
.. toctree::
   :maxdepth: 1

   content/installation
   content/quick_start
   content/handeling
   content/track
   content/manipulate
   content/memory
   content/numbering
   content/bugs
   content/licensing
