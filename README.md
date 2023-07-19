
I have made 41 testcases for my program. Each testcase is of 2 files (in and out). The out file is the expected outcome of the program given specific input files.
For each command there are error inputs and valid inputs: eg: "error.in" and "trivial.in". Some command which has optional flags also have "flag.in" files. The same applies to out files.
To get the coverage report, run "bash coverage.sh". I had to put python -m in front of "coverage run" since without it my coverage wont be showed, delete "python -m" and try to run the sh file again if there is any errors.
