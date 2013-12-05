#==============================================================================
# Time-stamp: <2013-12-05 10:31:29 jgp>
#------------------------------------------------------------------------------

This project contains MARCXML files for the ACO project.
Directory structure is as follows:

bin/                 stores scripts
marcxml/<partner>    stores source MARCXML files from partners
work/<dstamp>        stores .csv file with format specified below
                     contains all MARCXML files mentioned in the CSV file

CSV file format:
<header row>
<data rows>

header row = 003,001,handle
data   row = NNU,123456789,http://hdl.handle.net/2333.1/<NOID>


