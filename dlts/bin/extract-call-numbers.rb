#!/usr/bin/env ruby

require 'nokogiri'
require_relative '../lib/marcxml'

MIN_REQUIRED_ARGS = 1

def print_usage
  str = ["usage: #$0 <marcxml file 1>",
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


def clean_call_number(str)
  str.strip.gsub(/\s+/,' ')
end


m = Marcxml.new(ARGV[0])

puts "#{clean_call_number(m.get_050)},#{clean_call_number(m.get_082)},#{clean_call_number(m.get_090)},#{clean_call_number(m.get_852)}"

