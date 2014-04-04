require 'test_helper'
require 'open3'
require 'fileutils'

#class GenWorkDirsTest < Test::Unit::TestCase
class GenWorkDirsTest < MiniTest::Unit::TestCase

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

  UNWRITABLE_DIR  = 'test/wip/unwritable'
  NNC_V1          = 'test/wip/NNC_valid_1'
  NNC_V2          = 'test/wip/NNC_valid_2'
  COO_V1          = 'test/wip/COO_valid_1'
  COO_V2          = 'test/wip/COO_valid_2'
  WORK_DIR        = 'test/work'
  DNE_PATH        = 'this-path-does-not-exist'

  def test_valid_invocation
    o, e, s = Open3.capture3("#{COMMAND} #{NNC_V1} #{COO_V1}")
    assert(s == 0, "exit status: #{e}")
    assert('' == o, "stdout")
    assert('' == e, "stderr")
  end

  def test_with_incorrect_argument_count
    o, e, s = Open3.capture3("#{COMMAND}")
    assert(s != 0)
    assert(o == '')
    assert_match(/usage/, e)
    assert_match(/incorrect number of arguments/, e)
  end

  def test_with_unwritable_dir
    o, e, s = Open3.capture3("#{COMMAND} #{UNWRITABLE_DIR} #{NNC_V1}")
    assert(s != 0)
    assert(o == '')
    assert_match(/usage/, e)
    assert_match(/bad target directory/, e)
  end

  def test_with_non_existent_work_dir
    o, e, s = Open3.capture3("#{COMMAND} #{DNE_PATH} #{NNC_V1}")
    assert(s != 0)
    assert(o == '')
    assert_match(/usage/, e)
    assert_match(/bad target directory/, e)
  end

  def test_with_non_existent_wip_dir
    o, e, s = Open3.capture3("#{COMMAND} #{WORK_DIR} #{DNE_PATH}")
    assert(s != 0)
    assert(o == '')
    assert_match(/directory does not exist/, e)
  end

  def test_with_single_wip_dir
    o, e, s = Open3.capture3("#{COMMAND} #{WORK_DIR} #{NNC_V1}")
    today = Time.now.strftime("%Y%m%d")
    assert(s == 0)
    assert(File.exists?(File.join(WORK_DIR, "NNC")), "work/<003> subdirectory not created")
  end

  # def test_with_invalid_dir
  #   o, e, s = Open3.capture3("#{COMMAND} 'nyu_aco000003' 'SOURCE_ENTITY:TEXT' 'VERTICAL' 'LEFT_TO_RIGHT' 'RIGHT_TO_LEFT' invalid-dir-path")
  #   assert(s != 0, "incorrect exit status")
  #   assert(o == '')
  #   assert_match(/directory does not exist/, e, 'unexpected error message')
  # end

  # def test_invalid_se_type
  #   o, e, s = Open3.capture3("#{COMMAND} 'nyu_aco000003' 'INVALID' 'VERTICAL' 'LEFT_TO_RIGHT' 'RIGHT_TO_LEFT' #{VALID_TEXT}")
  #   assert(s != 0)
  #   assert(o == '')
  #   assert_match(/incorrect se type/, e, 'unexpected error message')
  # end

  # def test_invalid_binding_orientation
  #   o, e, s = Open3.capture3("#{COMMAND} 'nyu_aco000003' 'SOURCE_ENTITY:TEXT' 'INVALID' 'LEFT_TO_RIGHT' 'RIGHT_TO_LEFT' #{VALID_TEXT}")
  #   assert(s != 0)
  #   assert(o == '')
  #   assert_match(/incorrect binding orientation/, e, 'unexpected error message')
  # end

  # def test_invalid_scan_order
  #   o, e, s = Open3.capture3("#{COMMAND} 'nyu_aco000003' 'SOURCE_ENTITY:TEXT' 'HORIZONTAL' 'INVALID' 'RIGHT_TO_LEFT' #{VALID_TEXT}")
  #   assert(s != 0)
  #   assert(o == '')
  #   assert_match(/incorrect scan order/, e, 'unexpected error message')
  # end

  # def test_invalid_read_order
  #   o, e, s = Open3.capture3("#{COMMAND} 'nyu_aco000003' 'SOURCE_ENTITY:TEXT' 'HORIZONTAL' 'RIGHT_TO_LEFT' 'INVALID' #{VALID_TEXT}")
  #   assert(s != 0)
  #   assert(o == '')
  #   assert_match(/incorrect read order/, e, 'unexpected error message')
  # end

  # def test_missing_md_files
  #   o, e, s = Open3.capture3("#{COMMAND} 'nyu_aco000003' 'SOURCE_ENTITY:TEXT' 'HORIZONTAL' 'RIGHT_TO_LEFT' 'LEFT_TO_RIGHT' #{EMPTY_TEXT}")
  #   assert(s != 0)
  #   assert(o == '')
  #   assert_match(/missing or too many files ending in _mods\.xml/, e)
  #   assert_match(/missing or too many files ending in _marcxml\.xml/, e)
  #   assert_match(/missing or too many files ending in _metsrights\.xml/, e)
  #   assert_match(/missing or too many files ending in _eoc\.csv/, e)
  #   assert_match(/missing or too many files ending in _ztarget_m\.tif/, e)
  # end

  # def test_mismatched_master_dmaker_file_count
  #   o, e, s = Open3.capture3("#{COMMAND} 'nyu_aco000003' 'SOURCE_ENTITY:TEXT' 'HORIZONTAL' 'RIGHT_TO_LEFT' 'LEFT_TO_RIGHT' #{BAD_M_D_COUNT_TEXT}")
  #   assert(s != 0)
  #   assert(o == '')
  #   assert_match(/mismatch in master \/ dmaker file count/, e)
  # end

  # def test_mismatched_master_dmaker_file_prefixes
  #   o, e, s = Open3.capture3("#{COMMAND} 'nyu_aco000003' 'SOURCE_ENTITY:TEXT' 'HORIZONTAL' 'RIGHT_TO_LEFT' 'LEFT_TO_RIGHT' #{BAD_M_D_PREFIX_TEXT}")
  #   assert(s != 0)
  #   assert(o == '')
  #   assert_match(/prefix mismatch:/, e)
  # end

  # def test_output_with_valid_text
  #   new_xml, e, s = Open3.capture3("#{COMMAND} 'nyu_aco000003' 'SOURCE_ENTITY:TEXT' 'VERTICAL' 'LEFT_TO_RIGHT' 'RIGHT_TO_LEFT' #{VALID_TEXT}")
  #   assert(s == 0)
  #   old_xml, e, s = Open3.capture3("cat #{CANONICAL_XML}")
  #   new_xml_a = new_xml.split("\n")
  #   old_xml_a = old_xml.split("\n")

  #   new_xml_a.each_index do |i|
  #     new = new_xml_a[i].strip
  #     old = old_xml_a[i].strip

  #     # replace dates
  #     if /metsHdr/.match(new)
  #       timestamp_regex = /[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z/
  #       new.gsub!(timestamp_regex,'')
  #       old.gsub!(timestamp_regex,'')
  #     end
  #     assert(new == old, "xml mismatch: #{new} #{old}")
  #   end
  # end

end
