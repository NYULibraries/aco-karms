require 'nokogiri'
require 'open-uri'

class Marcxml

  # NNU = New York University
  # NNC = Columbia University
  # NIC = Cornell University
  # NjP = Princeton University
  # LeBAU = American University of Beirut
  # UaCaAUL = The American University in Cairo
  VALID_003_CODES = %w(NNU NNC NIC NjP LeBAU UaCaAUL)

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
    raise "marcxml file does not exist"  unless File.exist?(@path)
    raise "marcxml file is not readable" unless File.readable?(@path)
  end

  def validate_against_schema!
    xsd  = Nokogiri::XML::Schema(File.open(@schema_path))
    @doc = Nokogiri::XML(File.open(@path)) {|config| config.strict }

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

    # the MARC21/slim xmlns varies by document
    #   some  documents use the default 'xmlns' namespace
    #   other documents use the 'xmlns:marc'    namespace
    #
    # These differences are reflected in the Nokogiri XPath expressions:
    #   e.g.
    #     //xmlns:record/xmlns:controlfield
    #     //marc:record/marc:controlfield
    #
    # Nokogiri::XML::Document#namespaces is used to determine the proper
    #   namespace prefix to use in the XPath expressions.
    #
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
    #
    # use 'xmlns' if in default namespace, otherwise extract namespace prefix
    ns = key == "xmlns" ? key : key.sub("xmlns:",'')

    # assemble prefix for the controlfield Nokogiri XPath expression
    xpath_prefix = "//#{ns}:record/#{ns}:controlfield"

    # extract the controlfield 001 and 003 values
    @ctrl_001 = @doc.xpath("#{xpath_prefix}[@tag='001']").text
    @ctrl_003 = @doc.xpath("#{xpath_prefix}[@tag='003']").text

    # assert that controlfields are not missing or empty
    raise "missing controlfield 001" if @ctrl_001 == ''
    raise "missing controlfield 003" if @ctrl_003 == ''
    raise "unrecognized controlfield 003 : #{@ctrl_003}" unless VALID_003_CODES.include?(@ctrl_003)
  end
end
