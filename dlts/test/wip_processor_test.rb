require 'test_helper'

class WipProcessorTest < MiniTest::Unit::TestCase
  NNC_V1    = 'test/wip/NNC_valid_1'
  NNC_V2    = 'test/wip/NNC_valid_2'
  COO_V1    = 'test/wip/COO_valid_1'
  COO_V2    = 'test/wip/COO_valid_2'
  WORK_DIR  = 'test/work'
  DNE_PATH  = 'this-path-does-not-exist'
  TEST_NNC_ONE  = {work_root: WORK_DIR, wips: [Wip.new(NNC_V1)]}
  TEST_NNC_TWO  = {work_root: WORK_DIR, wips: [Wip.new(NNC_V1), Wip.new(NNC_V2)]}
  TEST_FOUR     = {work_root: WORK_DIR, wips: [Wip.new(NNC_V1), Wip.new(COO_V1), Wip.new(NNC_V2), Wip.new(COO_V2)]}
  C_NNC_ONE_CSV = 'test/canonical/handles_nnc_one.csv'
  C_NNC_TWO_CSV = 'test/canonical/handles_nnc_two.csv'
  C_COO_TWO_CSV = 'test/canonical/handles_coo_two.csv'

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
    assert_instance_of(WipProcessor, WipProcessor.new(TEST_NNC_ONE))
  end

  def test_wip_directory_does_not_exist
    err = assert_raises(RuntimeError) { Wip.new(DNE_PATH) }
    assert_match(/directory does not exist/, err.message)
  end

  def test_run_method_creates_directory_heirarchy
    date_str  = Time.now.strftime("%Y%m%d")

    w = WipProcessor.new(TEST_NNC_ONE)
    w.run
    assert(File.exists?(File.join(WORK_DIR, 'NNC')), "<003> dir not created")
    assert(File.exists?(File.join(WORK_DIR, 'NNC', "NNC_#{date_str}")), "<003>_<date_str> dir not created")
    assert(File.exists?(File.join(WORK_DIR, 'NNC', "NNC_#{date_str}", 'marcxml_in')), "marcxml dir not created")
  end

  def test_run_method_copies_marcxml_file
    date_str  = Time.now.strftime("%Y%m%d")

    w = WipProcessor.new(TEST_NNC_ONE)
    w.run
    exp = File.join(WORK_DIR, 'NNC', "NNC_#{date_str}", 'marcxml_in', "NNC_3076855_marcxml.xml")
    assert(File.exists?(exp), "marcxml file not copied")
    assert(FileUtils.cmp(exp, File.join(NNC_V1, 'data', 'columbia_CU58888896_marcxml.xml')))
  end

  def test_run_method_creates_csv_file
    date_str  = Time.now.strftime("%Y%m%d")

    w = WipProcessor.new(TEST_NNC_ONE)
    w.run
    exp = File.join(WORK_DIR, 'NNC', "NNC_#{date_str}", 'handles.csv')
    assert(File.exists?(exp), "csv file not created")
    assert(FileUtils.cmp(exp, C_NNC_ONE_CSV))
  end

  def test_run_method_creates_correct_csv_file_for_two_wips
    date_str  = Time.now.strftime("%Y%m%d")

    w = WipProcessor.new(TEST_NNC_TWO)
    w.run
    exp = File.join(WORK_DIR, 'NNC', "NNC_#{date_str}", 'handles.csv')
    assert(File.exists?(exp), "csv file not created")
    assert(FileUtils.cmp(exp, C_NNC_TWO_CSV))
  end

  def test_run_method_creates_correct_csv_files_for_four_wips_from_two_003s
    date_str  = Time.now.strftime("%Y%m%d")

    w = WipProcessor.new(TEST_FOUR)
    w.run
    exp_nnc = File.join(WORK_DIR, 'NNC', "NNC_#{date_str}", 'handles.csv')
    assert(File.exists?(exp_nnc), "NNC csv file not created")
    assert(FileUtils.cmp(exp_nnc, C_NNC_TWO_CSV))

    exp_coo = File.join(WORK_DIR, 'COO', "COO_#{date_str}", 'handles.csv')
    assert(File.exists?(exp_coo), "COO csv file not created")
    assert(FileUtils.cmp(exp_coo, C_COO_TWO_CSV))
  end


  MiniTest::Unit.after_tests do
    FileUtils.mkdir(WORK_DIR) unless File.exists?(WORK_DIR)
    FileUtils.touch(File.join(WORK_DIR, '.gitkeep'))
  end

end
