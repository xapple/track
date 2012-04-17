"""
This module can benchmark the performance of different I/O strategies
and helps make developement choices based on quantitative results.

We would like to measure three characteristics when creating SQLite files:
   * the size of resulting file,
   * the speed of file creation,
   * the speed of data access.

Use it like this::
    $ ipython
    > cd /dev/benchmarks
    > import compare
    > compare.run(state='before')
    [[[edit the source code of track]]]
    > import track
    > reload(track)
    > compare.run(state='after')
    > compare.plot_results()
    > cd compare.output_directory
    > ls
"""

# Built-in modules #
import os, time

# Internal modules #
import track
from track.common import Path, Timer, Filesize

# Output directory #
output_directory = "/scratch/local/daily/%s/" % os.environ['USER']
if not os.path.exists(output_directory): os.makedirs(output_directory)

# Input files #
input_files = {
    'SGA with 159':      {'path': Path('/db/chipseq/mm9/fts/Mus_EPD.sga')},
    'SGA with 121353':   {'path': Path('/db/chipseq/sacCer/albert07/H2AZ.sga')},
    'SGA with 5941142':  {'path': Path('/db/chipseq/hg18/barski07/H3K9me3.sga')},
}

################################################################################
def benchmark_creation(file):
    old_path = file['path']
    new_path = Path(output_directory + old_path.filename + '.sql')
    if os.path.exists(str(new_path)): os.remove(str(new_path))
    with Timer() as timer: track.convert(str(old_path), str(new_path))
    file['new_path'] = new_path
    return timer.total_time

def benchmark_access(file):
    with track.load(str(file['new_path'])) as t:
        with Timer() as timer:
            data = t.read()
            for entry in data: pass
    return timer.total_time

def benchmark_size(file):
    return Filesize(file['new_path'])

################################################################################
def run(state='before'):
    """Run all the benchmarks"""
    # Iterate on every file #
    for file in input_files.values():
        file[state+'_creation'] = benchmark_creation(file)
        file[state+'_access'] = benchmark_access(file)
        file[state+'_size'] = benchmark_size(file)

################################################################################
def plot_results(output_path = output_directory):
    """Plot the results of the benchmarks and create a PDF file
       at the given path using matplotlib"""
    import matplotlib, numpy
    matplotlib.use('Agg', warn=False)
    from matplotlib import pyplot
    for metric in ['creation', 'access', 'size']:
        # Preparation #
        fig = pyplot.figure()
        fig.text(0.96, 0.96, time.asctime(), horizontalalignment='right')
        fig.text(0.04, 0.96, 'track generated graph', horizontalalignment='left')
        axes = fig.add_subplot(111)
        axes.set_title('Track benchmark')
        # Axis title #
        if metric == 'creation': axes.set_ylabel('Creation time [seconds]')
        if metric == 'access': axes.set_ylabel('Access time [seconds]')
        if metric == 'size': axes.set_ylabel('File size [bytes]')
        # Data gathering #
        names = input_files.keys()
        series_before_y = [float(file['before_' + metric]) for file in input_files.values()]
        series_after_y = [float(file['after_' + metric]) for file in input_files.values()]
        # Step of 3: red dot, blue dot, empty space
        series_before_x = numpy.arange(0, 3*len(series_before_y), 3)
        series_after_x = numpy.arange(1, 3*len(series_after_y)+1, 3)
        # Plotting #
        axes.scatter(series_before_x, series_before_y, c='r', s=100, label='before')
        axes.scatter(series_after_x, series_after_y, s=100, label='after')
        axes.set_xticks((series_before_x+series_after_x)/2.)
        axes.set_xticklabels(names)
        axes.legend(loc=2)
        # Exporting #
        path = output_directory + metric + '_results.pdf'
        if os.path.exists(path): os.remove(path)
        fig.savefig(path, transparent=True)
        # Text dump #
        path = output_directory + metric + '_results.text'
        with open(path, 'w') as f:
            f.write('BEFORE\n')
            for label, file in input_files.items():
                f.write(label + ' ' + metric + ' ' + str(file['before_' + metric]) + '\n')
            f.write('AFTER\n')
            for label, file in input_files.items():
                f.write(label + ' ' + metric + ' ' + str(file['after_' + metric]) + '\n')
