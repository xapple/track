###################
Manipulating tracks
###################

Using only file paths
---------------------
Here is a short example where a new track is created containing the ``mean_score_by_feature`` computed on two other tracks::

    from gMiner.genomic_manip import mean_score_by_feature
    virtual_track = mean_score_by_feature('/tracks/pol2.sql', '/tracks/rib_prot.sql')
    virtual_track.export('/tmp/result.sql')

Using track objects
-------------------
You can also do the same thing by inputing track objects directly::

    import track
    from track.manipulate import mean_score_by_feature
    with track.load('/scratch/tracks/pol2.sql') as pol2:
        with track.load('/scratch/tracks/ribosome_proteins.sql') as rpgenes:
            virtual_track = mean_score_by_feature(pol2,rpgenes)
            virtual_track.export('/tmp/result.sql')

Chaining manipulations
----------------------
The beautiful thing about this is that operations can be chained one to an other without having to compute intermediary states. The following also works::

    import track
    from track.manipulate import overlap, complement
    with track.load('/scratch/genomic/tracks/pol2.sql') as pol2:
        with track.load('/scratch/genomic/tracks/rap1.sql') as rap1:
            virtual_track = complement(overlap(pol2,rap1))
            virtual_track.export('/tmp/result.sql')

.. automodule:: track.manipulate
