#!/usr/bin/env ruby
require_relative '../lib/marcxml'

MIN_REQUIRED_ARGS = 1

def print_usage
  str = ["usage: #$0 <marcxml file 1> [<marcxml file 2> ...]",
    "   <marcxml file 1> : first  MARCXML file to validate using ACO criteria",
    "   <marcxml file 2> : second MARCXML file to validate using ACO criteria",
    "   ...              : additional MARCXML files to validate",
    " ",
    "example:",
    "   #$0 foo.xml bar.xml",
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

  # instantiate Wip objects
  # N.B. the Wip.new raises an exception if there is a problem
  args_out[:marcxml_files] = []
  args_in.each do |f|
    unless File.exists?(f)
      errors << "File does not exist: #{f}"
      next
    end
    errors << "File is not readable: #{f}" unless File.readable?(f)

    args_out[:marcxml_files] << f
  end

  unless errors.empty?
    emsg = errors.join("\n")
    err_exit(emsg)
  end

  args_out
end

#------------------------------------------------------------------------------
# MAIN
#------------------------------------------------------------------------------
args = validate_and_extract_args(ARGV)

files   = args[:marcxml_files]

errors  = []
valid   = 0
invalid = 0

files.each do |f|
  begin
    Marcxml.new(f)
    valid += 1
  rescue => e
    errors << "#{f} : #{e.message}"
    invalid += 1
  end
end

emsg = "invalid state: number of files processed != valid + invalid"
raise emsg unless files.length == valid + invalid

puts "processed: #{files.length} valid: #{valid} invalid: #{invalid}"
err_exit(errors.join("\n")) unless errors.empty?

