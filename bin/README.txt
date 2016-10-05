------------------------------------------------------------------------------
Time-stamp: <2016-10-05 10:15:24 jgp>
------------------------------------------------------------------------------
How to run "gen-karms-report.sh" script on a Mac:

1.) open a Terminal window

2.) "cd" to the "aco-karms" project directory, e.g.,
    $ cd /path/to/aco-karms

3.) type the following command:
    $ ./bin/gen-karms-report.sh   # outputs report to the terminal

    You can redirect this output to a file as follows:
    $ ./bin/gen-karms-report.sh > karms-report.csv

    If you want to watch the report being output and also generate a file:
    $ ./bin/gen-karms-report.sh | tee karms-report.csv

