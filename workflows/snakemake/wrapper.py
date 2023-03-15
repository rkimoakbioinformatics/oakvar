# snakemake wrapper script for ov run command
import sys
import snakemake

from snakemake.shell import shell

# input file 
input = sys.argv[1]

# define optional arguments
annotator = []
reporter = []

# build ov run command
cmd = "ov run {}".format(input)

# Check for any specified annotator and reports names and add them to the command
if annotator:
    cmd += " -a {}".format(" ".join(annotator))
if reporter:
    cmd += " -t {}".format(" ".join(reporter))

# execute command
shell(cmd)
