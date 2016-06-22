#!/usr/bin/env ruby
require 'fileutils'
require_relative '../lib/marcxml'

MIN_REQUIRED_ARGS = 1

def print_usage
  str = ["usage: #$0 <marcxml file 1> [<marcxml file 2> ...]",
    "   <marcxml file 1> : first   MARCXML file check for missing call numbers",
    "   <marcxml file 2> : second  MARCXML file check for missing call numbers",
    "   ...              : additional MARCXML files to check",
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
present = 0
missing = 0
bad     = 0

files.each do |f|
  begin
    m = Marcxml.new(f)
    if m.is_050_empty? && m.is_090_empty?
      puts "#{f} : cannot find call number"
      missing += 1
    else
      present += 1
    end
  rescue => e
    errors << "#{f} : #{e.message}"
    bad += 1
  end
end

puts "processed: #{files.length} present: #{present} missing: #{missing} bad: #{bad}"
err_exit(errors.join("\n")) unless errors.empty?

emsg = "invalid state: number of files processed (#{files.length}) != present (#{present})  + missing (#{missing}) + bad (#{bad})"
raise emsg unless files.length == present + missing + bad

