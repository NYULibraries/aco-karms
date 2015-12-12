require 'test_helper'
require 'open3'
require 'fileutils'

class GenWorkDirsTest < MiniTest::Test

  COMMAND = 'ruby bin/gen-work-dirs.rb'

  # for each wip directory
  # - creates a /work/<003> directory if it does not exist
  # - creates a /work/<003>/<003>_<date stamp> directory if it DNE
  # - creates a /work/<003>/<003>_<date stamp>/marcxmk directory if it DNE
  # - creates the handles.csv file if it DNE and emits the header row
  # - copies the marcxml to the marcxml directory
  # - appends the WIP's <003>,<001>,<handle> to the csv file
  # exits 0 on success
  # exits non-zero on failure

  UNWRITABLE_DIR  = 'test/fixtures/wip/unwritable'
  NNC_V1          = 'test/fixtures/wip/NNC_valid_1'
  NNC_V2          = 'test/fixtures/wip/NNC_valid_2'
  NIC_V1          = 'test/fixtures/wip/NIC_valid_1'
  NIC_V2          = 'test/fixtures/wip/NIC_valid_2'
  WORK_DIR        = 'test/work'
  DNE_PATH        = 'this-path-does-not-exist'

  def create_work_dir
    FileUtils.mkdir(WORK_DIR) unless File.exist?(WORK_DIR)
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

  def test_valid_invocation
    o, e, s = Open3.capture3("#{COMMAND} #{WORK_DIR} #{NIC_V1}")
    assert(s.exitstatus == 0, "exit status: #{e}")
    assert('' == o, "stdout")
    assert('' == e, "stderr")
  end

  def test_with_incorrect_argument_count
    o, e, s = Open3.capture3("#{COMMAND}")
    assert(s.exitstatus != 0)
    assert(o == '')
    assert_match(/usage/, e)
    assert_match(/incorrect number of arguments/, e)
  end

  def test_with_unwritable_dir
    o, e, s = Open3.capture3("#{COMMAND} #{UNWRITABLE_DIR} #{NNC_V1}")
    assert(s.exitstatus != 0)
    assert(o == '')
    assert_match(/usage/, e)
    assert_match(/bad target directory/, e)
  end

  def test_with_non_existent_work_dir
    o, e, s = Open3.capture3("#{COMMAND} #{DNE_PATH} #{NNC_V1}")
    assert(s.exitstatus != 0)
    assert(o == '')
    assert_match(/usage/, e)
    assert_match(/bad target directory/, e)
  end

  def test_with_non_existent_wip_dir
    o, e, s = Open3.capture3("#{COMMAND} #{WORK_DIR} #{DNE_PATH}")
    assert(s.exitstatus != 0)
    assert(o == '')
    assert_match(/directory does not exist/, e)
  end

  MiniTest.after_run do
    FileUtils.mkdir(WORK_DIR) unless File.exist?(WORK_DIR)
    FileUtils.touch(File.join(WORK_DIR, '.gitkeep'))
  end

end
