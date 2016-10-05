------------------------------------------------------------------------------
Time-stamp: <2016-10-05 10:45:48 jgp>
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


CSV Report Format:
------------------
The first line of the report is the header line:
  institution,original_bsn,se_map,pub_batch,oclc,digital_bsn,notes

The subsequent lines are generated, one per original BSN.
e.g.,

  LeBAU,b12366031,aub_aco000002,LeBAU_20151212,,,
  LeBAU,b12377740,aub_aco000005:v.1|aub_aco000006:v.2|aub_aco000007:v.3|aub_aco000008:v.4|aub_aco000009:v.5|aub_aco000010:v.6,LeBAU_20151212,,,
  LeBAU,b12395833,aub_aco000004,LeBAU_20151212,,,


Multi-vols are grouped in the se_map field and follow this template:
  <digitization id book 1>:<book 1 label>|<digization id book 2>:<book 2 label>|<digitization id book 3>...


Sample Output (indented to show report contents):
-------------------------------------------------
  institution,original_bsn,se_map,pub_batch,oclc,digital_bsn,notes
  LeBAU,b12366031,aub_aco000002,LeBAU_20151212,,,
  LeBAU,b12377740,aub_aco000005:v.1|aub_aco000006:v.2|aub_aco000007:v.3|aub_aco000008:v.4|aub_aco000009:v.5|aub_aco000010:v.6,LeBAU_20151212,,,
  LeBAU,b12395833,aub_aco000004,LeBAU_20151212,,,

------------------------------------------------------------------------------
end of README
------------------------------------------------------------------------------

