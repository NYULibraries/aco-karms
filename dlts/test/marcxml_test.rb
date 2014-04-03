require 'test_helper'
class MarcxmlTest < MiniTest::Unit::TestCase

  VALID_MARCXML_PATH      = 'test/marcxml/valid'
  INVALID_001_PATH        = 'test/marcxml/invalid_001'
  EMPTY_MARCXML_PATH      = 'test/marcxml/empty'
  DNE_MARCXML_PATH        = 'this/path/does/not/exist'
  UNREADABLE_MARCXML_PATH = 'test/marcxml/unreadable'

  def test_class
    assert_instance_of(Marcxml, Marcxml.new(VALID_MARCXML_PATH))
  end

  def test_empty_marcxml_file
    err = assert_raises(RuntimeError) { Marcxml.new(EMPTY_MARCXML_PATH) }
    assert_match(/marcxml validation error/, err.message)
  end

  def test_nonexistent_marcxml_file
    err = assert_raises(RuntimeError) { Marcxml.new(DNE_MARCXML_PATH) }
    assert_match(/marcxml file does not exist/, err.message)
  end

  def test_unreadable_marcxml_file
    File.chmod( 0000, UNREADABLE_MARCXML_PATH)
    err = assert_raises(RuntimeError) { Marcxml.new(UNREADABLE_MARCXML_PATH) }
    assert_match(/marcxml file is not readable/, err.message)
  end

  def test_marcxml_get_003
    h = Marcxml.new(VALID_MARCXML_PATH)
    assert(h.get_003 == "COO")
  end


  # restore read/write permissions on test file
  MiniTest::Unit.after_tests { File.chmod( 0644, UNREADABLE_MARCXML_PATH) }

=begin

  def test_marcxml_get_001
    h = Marcxml.new(VALID_MARCXML_PATH)
    assert(h.marcxml == "2333.1/abdcde")
  end

  def test_marcxml_get_003
    h = Marcxml.new(VALID_MARCXML_PATH)
    assert(h.marcxml == "2333.1/abdcde")
  end

=end

end
