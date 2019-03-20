import argparse
import subprocess
import matplotlib.pyplot as plt
import sys
import os
import pandas as pd
from shutil import which
import re
from md_utils.fill_tpl import OUT_DIR, TPL_VALS, fill_save_tpl
from md_utils.md_common import (InvalidDataError, warning,
                                IO_ERROR, GOOD_RET, INPUT_ERROR, INVALID_DATA, read_tpl)

TPL_PATH = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + '/tests/test_data/scaling')
## Dictionary Keywords
WALLTIME = 'walltime'
NUM_PROCS = 'num_procs'
MEM = 'mem'
JOB_NAME = 'job_name'
NUM_NODES = 'num_nodes'
# Patterns
OUT_PAT = re.compile(r"^outputname.*")

# Defaults
DEF_NAME = 'scaling'


def proc_args(keys):
    tpl_vals = {}

    tpl_vals[WALLTIME] = keys.walltime
    tpl_vals[NUM_PROCS] = keys.num_procs
    tpl_vals[MEM] = keys.memory
    tpl_vals[JOB_NAME] = keys.job_name
    tpl_vals[NUM_NODES] = keys.num_nodes

    return tpl_vals


def make_file(basename, n_list):
    for n in n_list:
        with open(filename, 'w') as fout:
            # makes the file
            subprocess.call(["qsub", filename])
    # TODO: Make this work
    # TODO: Loop over nodes and processors, but only use full multiple nodes


def make_analysis(basename, n_list, scheduler):
    # TODO: I'm not sure what this will look like yet, but it will include namd_log_proc and the python plotting bit
    # I actually think it will be simpler to read all of the data into the plotting function rather than preprocessing with col_stats, which loses the filename
    # Decision: job that searches for the existence of all the logs. If it finds them, submit analysis job for 10 minutes later, otherwise resubmit itself.
    # This solution is somewhat vulnerable to failed jobs, but that's the user's responsibility.
    # Alternatively we could learn how to parse the scheduler output
    # set variables based on the scheduler type
    if scheduler == 'pbs':
        ext = '.pbs'
        submit = 'qsub'
        tpl = os.path.join(TPL_PATH)
    elif scheduler == 'slurm':
        ext = '.job'
        submit = 'sbatch'
    analysis_jobfile = basename + '_analysis' + ext
    with open(analysis_jobfile, 'w') as fout:
        print("hello world")


# "for file in ${files[@]}
# "do
# "   namd_log_proc --stats -p file
# "done

def plot_scaling(list_of_files):
    # TODO: Make a beautiful scaling plot
    # TODO: Some preprocessing needs to be done with output from namd_log_proc
    list = []
    for file in list_of_files:
        df = pd.read_csv(file, header=0, index_col=None)
        list.append(df)
    frame = pd.concat(list, ignore_index=True)


def parse_cmdline(argv):
    """
    Returns the parsed argument list and return code.
    `argv` is a list of arguments, or `None` for ``sys.argv[1:]``.
    """
    if argv is None:
        argv = sys.argv[1:]

    # initialize the parser object:
    # TODO: Add description and arguments, should include name, config file, runtime, maybe a template job file? Also scheduler but we can try to autodetect it as well
    # TODO: Add an option to just replot
    # TODO: create the joblist in the proc_args step and pass it around
    parser = argparse.ArgumentParser(
        description='Automated submission and analysis of scaling data for a provided program')
    parser.add_argument("-n", "--name", help="Basename for the scaling files. Default is {}.".format(DEF_NAME),
                        default=DEF_NAME)

    args = None
    try:
        args = parser.parse_args(argv)
        # Automatic scheduler detection
        if which('qsub'):
            args.scheduler = 'pbs'
            job_ext = '.pbs'
        elif which('sbatch'):
            args.scheduler = 'slurm'
            job_ext = '.job'

        args.filelist = []
        for num in args.num_procs:
            filename = args.name + '_' + num + '.' + job_ext
            args.filelist.append(filename)
    except IOError as e:
        warning(e)
        parser.print_help()
        return args, IO_ERROR
    except (InvalidDataError, SystemExit) as e:
        if hasattr(e, 'code') and e.code == 0:
            return args, GOOD_RET
        warning(e)
        parser.print_help()
        return args, INPUT_ERROR

    return args, GOOD_RET


def main(argv=None):
    # Read input
    args, ret = parse_cmdline(argv)
    if ret != GOOD_RET or args is None:
        return ret

    submit_list = []
    # try:
    #     # generate and submit job files
    #     submit = make_file(num_procs)
    #
    #     make_analysis()
    #     subprocess.call(["qsub", analysis_script])
    #     # qsub -a $(date -d '5 minutes' "+%H%M") resubmit.pbs
    #     # sbatch --begin=now+10minutes
    #
    # except IOError as e:
    #     warning("Problems reading file:", e)
    #     return IO_ERROR
    # except (ValueError, InvalidDataError) as e:
    #     warning("Problems reading data:", e)
    #     return INVALID_DATA

    return GOOD_RET  # success


if __name__ == '__main__':
    status = main()
    sys.exit(status)