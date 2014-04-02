#!/usr/bin/env ruby

=begin
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
A list of <partner>/aco/wip/ie directory paths to process

WIP prerequisites:
* handle file exists
* data/<ie UUID>_marcxml.xml
* each marcxml file is valid
* each marcxml file contains data in the 003 and 001 fields


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
=end

MIN_REQUIRED_ARGS = 2

def print_usage
  str = ["usage: #$0 <target dir> <ie WIP dir 1> [<ie WIP dir 2> ...]",
         "   <target dir>   : directory under which to create sub directories",
         "   <ie WIP dir 1> : first Intellectual Entity WIP directory",
         "   <ie WIP dir 2> : second Intellectual Entity WIP directory",
         "   ...            : additional Intellectual Entity WIP directories",
         " ",
         "example:",
         "   #$0 work wip/ie/foo wip/ie/bar wip/ie/baz wip/ie/quux",
         " "]
  $stderr.puts str.join("\n")
end

def usage_err_exit(msg = nil)
  $stderr.puts(msg) unless msg.nil?
  print_usage
  exit 1
end

def err_exit(msg = nil)
  $stderr.puts(msg) unless msg.nil?
  exit 1
end

def validate_and_extract_args(args_in)
  args_out = {}
  errors   = []

  # argument count correct?
  emsg = "incorrect number of arguments"
  usage_err_exit(emsg) unless args_in.length >= MIN_REQUIRED_ARGS

  candidate = args_in.shift
  emsg = "bad target directory"
  unless Dir.exists?(candidate) && File.writable?(candidate)
    usage_err_exit(emsg)
  end
end

#------------------------------------------------------------------------------
# MAIN
#------------------------------------------------------------------------------
args = validate_and_extract_args(ARGV)
