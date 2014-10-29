require 'test_helper'
class HandleTest < MiniTest::Unit::TestCase

  VALID_HANDLE_PATH      = 'test/fixtures/handle/valid'
  INVALID_HANDLE_PATH    = 'test/fixtures/handle/invalid'
  EMPTY_HANDLE_PATH      = 'test/fixtures/handle/empty'
  DNE_HANDLE_PATH        = 'this/path/does/not/exist'
  UNREADABLE_HANDLE_PATH = 'test/fixtures/handle/unreadable'

  # restore read/write permissions on test file
  def teardown
    File.chmod( 0644, UNREADABLE_HANDLE_PATH)
  end

  def test_class
    assert_instance_of(Handle, Handle.new(VALID_HANDLE_PATH))
  end

  def test_valid
    assert(Handle.new(VALID_HANDLE_PATH))
  end

  def test_empty_handle_file
    err = assert_raises(RuntimeError) { Handle.new(EMPTY_HANDLE_PATH) }
    assert_match(/handle file empty or has more than one line/, err.message)
  end

  def test_invalid_handle_file
    err = assert_raises(RuntimeError) { Handle.new(INVALID_HANDLE_PATH) }
    assert_match(/incorrect handle format/, err.message)
  end

  def test_nonexistent_handle_file
    err = assert_raises(RuntimeError) { Handle.new(DNE_HANDLE_PATH) }
    assert_match(/handle file does not exist/, err.message)
  end

  def test_unreadable_handle_file
    File.chmod( 0000, UNREADABLE_HANDLE_PATH)
    err = assert_raises(RuntimeError) { Handle.new(UNREADABLE_HANDLE_PATH) }
    assert_match(/handle file is not readable/, err.message)
  end

  def test_handle_method
    h = Handle.new(VALID_HANDLE_PATH)
    assert(h.handle == "2333.1/abdcde")
  end

  def test_prefix_method
    h = Handle.new(VALID_HANDLE_PATH)
    assert(h.prefix == "2333.1")
  end

  def test_suffix_method
    h = Handle.new(VALID_HANDLE_PATH)
    assert(h.suffix == "abdcde")
  end

  def test_to_url_method
    h = Handle.new(VALID_HANDLE_PATH)
    assert(h.to_url == "http://hdl.handle.net/2333.1/abdcde")
  end

end
