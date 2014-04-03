require 'nokogiri'
require 'open-uri'

class Marcxml
  def initialize(path)
    @path        = path.dup
    @schema_path = nil
    @doc         = nil
    @ctrl_003    = nil
    @ctrl_001    = nil

    get_schema_path
    validate_path!
    validate_against_schema!
    extract_ctrl!
  end

  def get_001
    @ctrl_001
  end

  def get_003
    @ctrl_003
  end

  private
  def get_schema_path
    this_file_path = File.dirname(File.expand_path(__FILE__))
    xsd_rel_path   = File.join(this_file_path, '..', 'xsd', 'MARC21slim.xsd')

    # clean up path
    @schema_path = File.expand_path(xsd_rel_path)
  end

  def validate_path!
    # check that marcxml exists and is readable
    raise "marcxml file does not exist"  unless File.exists?(@path)
    raise "marcxml file is not readable" unless File.readable?(@path)
  end

  def validate_against_schema!
    xsd  = Nokogiri::XML::Schema(File.open(@schema_path))
    @doc = Nokogiri::XML(File.open(@path))

    error_array = xsd.validate(@doc)
    unless error_array.empty?
      emsg ="marcxml validation error: \n"
      emsg += error_array.join("\n")

      raise emsg
    end
  end

  def extract_ctrl!
    @ctrl_001 = @doc.xpath("//xmlns:record/xmlns:controlfield[@tag='001']").text
    @ctrl_003 = @doc.xpath("//xmlns:record/xmlns:controlfield[@tag='003']").text
    raise "missing controlfield 001" if @ctrl_001 == ''
    raise "missing controlfield 003" if @ctrl_003 == ''
  end

end
