require 'test_helper'

class WipProcessorTest < MiniTest::Unit::TestCase
  NNC_V1    = 'test/wip/NNC_valid_1'
  NNC_V2    = 'test/wip/NNC_valid_2'
  COO_V1    = 'test/wip/COO_valid_1'
  COO_V2    = 'test/wip/COO_valid_2'
  WORK_DIR  = 'test/work'
  DNE_PATH  = 'this-path-does-not-exist'
  TEST_ONE  = {work_root: WORK_DIR, wips: [NNC_V1]}

  def create_work_dir
    FileUtils.mkdir(WORK_DIR) unless File.exists?(WORK_DIR)
    FileUtils.touch(File.join(WORK_DIR, '.gitkeep'))
  end

  def destroy_work_dir
    FileUtils.remove_dir(WORK_DIR)
  end

  def setup
    create_work_dir
  end

  def teardown
    destroy_work_dir
  end

  def test_class
    assert_instance_of(WipProcessor, WipProcessor.new(TEST_ONE))
  end

  def test_wip_directory_does_not_exist
    err = assert_raises(RuntimeError) { Wip.new(DNE_PATH) }
    assert_match(/directory does not exist/, err.message)
  end

  MiniTest::Unit.after_tests do
    FileUtils.mkdir(WORK_DIR) unless File.exists?(WORK_DIR)
    FileUtils.touch(File.join(WORK_DIR, '.gitkeep'))
  end

=begin
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
=end
end
