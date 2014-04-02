require 'test/unit'
require 'open3'

class GenWorkDirs < Test::Unit::TestCase

  COMMAND = 'ruby bin/gen-work-dirs.rb'


# it creates a directory if there are some IEs that have not been processed
# it emits the header row successfully
# it parses the MARCXML correctly
# it emits the 003,001, and handle fields correctly
# it does not create a directory if all files have already been processed
# it reports the number of files process to stderr
# it exits with zero status on success
# it exits with non-zero status on failure


  # VALID_TEXT          = 'test/texts/valid'
  # EMPTY_TEXT          = 'test/texts/empty-dir'
  # BAD_M_D_COUNT_TEXT  = 'test/texts/bad-m-d-file-count'
  # BAD_M_D_PREFIX_TEXT = 'test/texts/bad-m-d-prefix'
  # CANONICAL_XML       = 'test/canonical/valid_mets.xml'

  def test_with_incorrect_argument_count
    o, e, s = Open3.capture3("#{COMMAND}")
    assert(s != 0)
    assert(o == '')
    assert_match(/usage/, e)
    assert_match(/incorrect number of arguments/, e)
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
