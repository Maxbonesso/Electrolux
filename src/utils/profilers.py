import cProfile
import os
import time
from typing import Optional, Any, Tuple, Dict, Callable


class ProfilingException(Exception):
    def __init__(self):
        super().__init__('ProfilingException')

class Timer(object):
    """
    Helper class to measure a time interval.

    A simple use case is:

    >>> with Timer('foo_stuff'):
    >>>     # do some stuff
    """

    def __init__(self, name: Optional[str] = None):
        self.timer_name = name

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, exit_type, value, traceback):
        if self.timer_name is not None:
            print('[PROF] {:s}'.format(self.timer_name))
        print('[PROF] Elapsed: {:.4f}'.format(time.time() - self.start_time))


class PerfProfiler:
    """
    Analyse performance analysis using `cProfile` and `pyprof2calltree`.
    """

    def __init__(self, name='my_script') -> None:
        """
        :param name: output file name.
        """
        self.output_filename = name + '.pstats'
        self.profiler = cProfile.Profile()
        self.active = False

    def profile(self, fun: Callable, *args, **kwargs) -> Any:
        """
        Profile given function.

        :param fun: function to test.
        :param args: function arguments.
        :param kwargs: key-worded function arguments.
        :return:
        """
        self.start_profiling()
        try:
            res = fun(*args, **kwargs)
        except ProfilingException:
            res = None
        self.stop_profiling()
        return res

    def start_profiling(self) -> None:
        """
        Start performance analysis.
        """
        self.active = True
        self.profiler.enable()
        print('[PROF] Analysing.. mmh ..')

    def stop_profiling(self) -> None:
        """
        Stop performance analysis.
        """
        if self.active:
            self.profiler.disable()
            self.profiler.dump_stats(self.output_filename)
            print('\n')
            os.system('pyprof2calltree -i {:s}'.format(self.output_filename))
            self.active = False
            print('[PROF] Report performed.')
        else:
            print('[PROF] I am actually not working.')


# from src.utils.profilers import PerfProfiler
# prof = PerfProfiler('CIRCLES')
# prof.start_profiling()
# prof.stop_profiling()


class BCOLORS:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def yellow_log(msg):
    print(BCOLORS.WARNING + msg + BCOLORS.ENDC)


def pink_log(msg):
    print(BCOLORS.HEADER + msg + BCOLORS.ENDC)


def blue_log(msg):
    print(BCOLORS.OKBLUE + msg + BCOLORS.ENDC)


def green_log(msg):
    print(BCOLORS.OKGREEN + msg + BCOLORS.ENDC)


def red_log(msg):
    print(BCOLORS.FAIL + msg + BCOLORS.ENDC)
