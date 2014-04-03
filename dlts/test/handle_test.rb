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

  def test_valid_invocation
    assert_instance_of(Handle, Handle.new(VALID_HANDLE_PATH))
  end


end
