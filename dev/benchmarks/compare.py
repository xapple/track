"""
This module can benchmark the performance of different I/O strategies
and helps make developement choices based on quantitative results.

We would like to measure three characteristics when creating SQLite files:
   * the size of resulting file,
   * the speed of file creation,
   * the speed of data access.
"""

# Built-in modules #
import os, time

# Internal modules #
import track
from track.common import Path, Timer, Filesize

# Output directory #
output_directory = "/scratch/ul/daily/%s/" % os.environ['USER']
if not os.path.exists(output_directory): os.makedirs(output_directory)

# Input files #
input_files = {
    'Sample SGA 1':   {'path': Path('/db/chipseq/hg18/barski07/H3K9me3.sga')},
}

################################################################################
def benchmark_creation(file):
    old_path = file['path']
    new_path = Path(output_directory + old_path.filename + '.sql')
    if os.path.exists(new_path): os.remove(new_path)
    with Timer() as t: track.convert(str(old_path), str(new_path))
    file['new_path'] = new_path
    return t.total_time

def benchmark_access(file):
    with track.load(str(file['new_path'])):
        with Timer() as t:
            data = track.read()
            for entry in data: pass
    return t.total_time

def benchmark_size(file):
    return Filesize(file['new_path'])

################################################################################
def run(path, state='before'):
    """Run all the benchmarks"""
    # Iterate on every file #
    for file in input_files.items():
        file[state+'_creation'] = benchmark_creation(file)
        file[state+'_access'] = benchmark_access(file)
        file[state+'_size'] = benchmark_size(file)
    # Print the results #
    for label, file in input_files.values():
        print label, 'creation:', file['creation'], 'seconds'
        print label, 'access:', file['access'], 'seconds'
        print label, 'size:', file['size']

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
        series_before_y = [file['before_'+metric] for file in input_files]
        series_after_y = [file['after_'+metric] for file in input_files]
        # Step of 3: red dot, blue dot, empty space
        series_before_x = numpy.arange(0, 3*len(series_before_y), 3)
        series_after_x = numpy.arange(1, 3*len(series_after_y)+1, 3)
        # Plotting #
        axes.scatter(series_before_x, series_before_y, c='r', s=100)
        axes.scatter(series_after_x, series_after_y, s=100)
        axes.xticks((series_before_x+series_after_x)/2., names)
        # Exporting #
        fig.savefig(output_directory + metric + '_results.pdf', transparent=True)
