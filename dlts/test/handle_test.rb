require 'test_helper'
class HandleTest < MiniTest::Unit::TestCase

  # it should be invalid with an empty handle file
  # it should return the proper prefix
  # it should return the proper suffix
  # it should be invalid with an invalid handle
  # it should be invalid if there is more than one handle
  # handle.to_s
  # handle.prefix
  # handle.suffix
  # handle.to_hdl
  # handle.to_url

  VALID_HANDLE_PATH   = 'test/handle/valid'
  INVALID_HANDLE_PATH = 'test/handle/invalid'
  EMPTY_HANDLE_PATH   = 'test/handle/empty'
  DNE_HANDLE_PATH     = 'this/path/does/not/exist'

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

end
