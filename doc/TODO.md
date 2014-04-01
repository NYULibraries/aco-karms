development plan:
-----------------

output:
------
a directory work/<yyyy-mm-dd>
in the work directory: 
yyyy-mm-dd.csv containing 003,001,handle
a set of MARCXML files.


input:
------
<partner>/aco/wip directories

each ie WIP directory has:
handle
data/<ie UUID>_marcxml.xml
each marcxml file is valid
each marcxml file contains data in the 003 and 001 fields.


flow:
----
aggregate list of IEs that have been digitized but have not been sent to KARMS
if list is not empty
  create subdirectory work/<yyyy-mm-dd>
  emit header row into file work/<yyyy-mm-dd>/<yyyy-mm-dd>.csv
  for each ie
    - open ie marcxml file
	- extract 001 and 003 fields
	- copy marcxml file from source to work/<yyyy-mm-dd>/<003>-<001>.xml
	- read handle file
	- emit <003>,<001>,http://hdl.handle.net/<handle>


tests:
-----
it creates a directory if there are some IEs that have not been processed
it emits the header row successfully
it parses the MARCXML correctly
it emits the 003,001, and handle fields correctly
it does not create a directory if all files have already been processed
it reports the number of files process to stderr
it exits with zero status on success
it exits with non-zero status on failure


questions:
----------
How to tell if a BSN has already been processed, or it needs to be reprocessed?
