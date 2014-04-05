#!/usr/bin/env ruby
require_relative '../lib/wip'
require_relative '../lib/wip_processor'

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

def target_dir_valid?(d)
  Dir.exists?(d) && File.writable?(d)
end

def ie_dir_valid?(ie)
  wip = Wip.new(ie)
end


def validate_and_extract_args(args_in)
  args_out = {}
  errors   = []

  # argument count correct?
  emsg = "incorrect number of arguments"
  usage_err_exit(emsg) unless args_in.length >= MIN_REQUIRED_ARGS

  # validate target directory
  candidate = args_in.shift
  emsg = "bad target directory"
  usage_err_exit(emsg) unless target_dir_valid?(candidate)
  args_out[:work_root] = candidate

  # instantiate Wip objects
  # N.B. the Wip.new raises an exception if there is a problem
  args_out[:wips] = []
  args_in.each do |wip_dir|
    w = Wip.new(wip_dir)
    args_out[:wips] << w
  end

  args_out
end

#------------------------------------------------------------------------------
# MAIN
#------------------------------------------------------------------------------
args = validate_and_extract_args(ARGV)

wp = WipProcessor.new(args)
wp.run

