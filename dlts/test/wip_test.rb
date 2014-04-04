require 'test_helper'

class WipTest < MiniTest::Unit::TestCase
  # the directory must exist
  # the directory must be readable
  # it must have a valid handle file
  # it must have one MARCXML file
  # it returns a marcxml object
  # it returns a handle object

  NNC_V1             = 'test/wip/NNC_valid_1'
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

  def test_marcxml_path_method
    w = Wip.new(NNC_V1)
    assert(w.marcxml_path == File.join(NNC_V1, 'data', 'columbia_CU58888896_marcxml.xml'))
  end
end
