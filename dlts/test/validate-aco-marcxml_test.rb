require 'test_helper'
require 'open3'

#class GenWorkDirsTest < Test::Unit::TestCase
class ValidateAcoMarcxml < MiniTest::Unit::TestCase

  COMMAND = 'ruby bin/validate-aco-marcxml.rb'

  VALID_MARCXML_PATH        = 'test/marcxml/valid'
  INVALID_001_PATH          = 'test/marcxml/invalid_001'
  INVALID_003_PATH          = 'test/marcxml/invalid_003'
  VALID_DEFAULT_NS_PATH     = 'test/marcxml/default_ns'
  VALID_NON_DEFAULT_NS_PATH = 'test/marcxml/non_default_ns'
  EMPTY_MARCXML_PATH        = 'test/marcxml/empty'
  DNE_MARCXML_PATH          = 'this/path/does/not/exist'
  UNREADABLE_MARCXML_PATH   = 'test/marcxml/unreadable'

  def test_valid_invocation
    o, e, s = Open3.capture3("#{COMMAND} #{VALID_MARCXML_PATH}")
    assert(s == 0, "exit status: #{e}")
    assert("processed: 1 valid: 1 invalid: 0\n" == o, "stdout was: '#{o}'")
    assert('' == e, "stderr")
  end

  def test_with_incorrect_argument_count
    o, e, s = Open3.capture3("#{COMMAND}")
    assert(s != 0)
    assert(o == '')
    assert_match(/usage/, e)
    assert_match(/incorrect number of arguments/, e)
  end

  def test_with_non_existent_file
    o, e, s = Open3.capture3("#{COMMAND} #{DNE_MARCXML_PATH}")
    assert(s != 0)
    assert(o == '')
    assert_match(/File does not exist/, e)
  end

  def test_unreadable_marcxml_file
    File.chmod( 0000, UNREADABLE_MARCXML_PATH)
    o, e, s = Open3.capture3("#{COMMAND} #{UNREADABLE_MARCXML_PATH}")
    assert(s != 0)
    assert(o == '')
    assert_match(/File is not readable/, e)
  end

  def test_multiple_valid_files
    o, e, s = Open3.capture3("#{COMMAND} #{VALID_MARCXML_PATH} #{VALID_DEFAULT_NS_PATH} #{VALID_NON_DEFAULT_NS_PATH}")
    assert(s == 0, "exit status: #{e}")
    assert("processed: 3 valid: 3 invalid: 0\n" == o, "stdout was: '#{o}'")
    assert('' == e, "stderr")
  end

#  def test_multiple_valid_and_invalid_files

  # restore read/write permissions on test file
  MiniTest::Unit.after_tests { File.chmod( 0644, UNREADABLE_MARCXML_PATH) }


end
