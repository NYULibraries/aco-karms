require 'test_helper'

class WipTest < MiniTest::Unit::TestCase
  # the directory must exist
  # the directory must be readable
  # it must have a valid handle file
  # it must have one MARCXML file
  # it returns a marcxml object
  # it returns a handle object

  NNC_V1             = 'test/wip/NNC_valid_1'
  COO_V1             = 'test/wip/COO_valid_1'
  I_MARCXML          = 'test/wip/invalid_marcxml'
  I_MARCXML_NO_003   = 'test/wip/invalid_marcxml_missing_003'
  I_NO_HANDLE        = 'test/wip/missing_handle'
  I_NO_MARCXML       = 'test/wip/missing_marcxml'
  I_TOO_MANY_MARCXML = 'test/wip/too_many_marcxml'
  DNE_PATH           = 'this-path-does-not-exist'

  def test_class
    assert_instance_of(Wip, Wip.new(NNC_V1))
  end

  def test_wip_directory_does_not_exist
    err = assert_raises(RuntimeError) { Wip.new(DNE_PATH) }
    assert_match(/directory does not exist/, err.message)
  end

  def test_handle_file_missing
    err = assert_raises(RuntimeError) { Wip.new(I_NO_HANDLE) }
    assert_match(/handle file does not exist/, err.message)
  end

  def test_marcxml_file_missing
    err = assert_raises(RuntimeError) { Wip.new(I_NO_MARCXML) }
    assert_match(/marcxml file count != 1/, err.message)
  end

  def test_marcxml_too_many_marcxml_files
    err = assert_raises(RuntimeError) { Wip.new(I_TOO_MANY_MARCXML) }
    assert_match(/marcxml file count != 1/, err.message)
  end

  def test_marcxml_missing_003_controlfield
    err = assert_raises(RuntimeError) { Wip.new(I_MARCXML_NO_003) }
    assert_match(/missing controlfield 003/, err.message)
  end

  def test_handle_method
    w = Wip.new(NNC_V1)
    assert(Handle, w.handle)
  end

  def test_marcxml_method
    w = Wip.new(NNC_V1)
    assert(Marcxml, w.marcxml)
  end


=begin
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
=end
end
