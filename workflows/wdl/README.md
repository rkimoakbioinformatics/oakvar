# Oakvar workflow
- In this work flow you can find wdl scripts to automate your oak var installation and setup.
- You will get a wdl script for an automated workflow example, as well.
# Before you start
1. You might run oakvar and cromwell in a conda environment as such the dependencies are installed:
    - You can install conda from here if you are working on linux or wsl on windows [conda installation](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html)
    - After installing conda you can install cromwell using this command `conda install -c bioconda cromwell`
2. If you are a windows or Mac user:
    - make sure to uncomment line 34 in run_example.wdl file in  annotation task that contains 'export TMPDIR=/tmp' in order to create a tmp dir and not run into any error.
# How to run OakVar automated WDL scripts: 
After successfuly installing conda and cromwell via conda you can simply use the command: `cromwell run <file_name>`