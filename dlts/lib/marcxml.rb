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
    key = @doc.namespaces.key("http://www.loc.gov/MARC21/slim")
    raise "unable to identify MARC21 namespace" if key.nil?

    # the xmlns varies by document
    # some documents use the default namespace, 'xmlns' for MARC21/slim
    # while other documents use 'xmlns:marc'
    # MARC21/slim is the default namespace, then we need 'xmlns' as the
    # namespace for Nokogiri xpaths.
    # if the MARC21/slim namespace is NOT the default, then
    # strip off the leading 'xmlns:' and extract the namespace prefix.
    # e.g.,
    #
    #   h = @columbia_doc.namespaces
    #     => {"xmlns"=>"http://www.loc.gov/MARC21/slim"}
    #   h.key("http://www.loc.gov/MARC21/slim")
    #     => "xmlns"
    #
    #   nyu_h = @nyu_doc.namespaces
    #     => {"xmlns:marc"=>"http://www.loc.gov/MARC21/slim"}
    #   nyu_h.key("http://www.loc.gov/MARC21/slim")
    #     => "xmlns:marc"
    #
    ns = key == "xmlns" ? key : key.sub("xmlns:",'')

    # assemble prefix for the controlfield Nokogiri XPath expression
    xpath_prefix = "//#{ns}:record/#{ns}:controlfield"

    # extract the controlfield 001 and 003 values
    @ctrl_001 = @doc.xpath("#{xpath_prefix}[@tag='001']").text
    @ctrl_003 = @doc.xpath("#{xpath_prefix}[@tag='003']").text

    # assert that controlfields are not missing or empty
    raise "missing controlfield 001" if @ctrl_001 == ''
    raise "missing controlfield 003" if @ctrl_003 == ''
  end

end
