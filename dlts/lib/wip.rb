# prototype
# ultimately:
#  nyudl:ie:wip
require_relative './marcxml'
require_relative './handle'

class Wip
  attr_reader :errors


  def initialize(path)
    @path     = path.dup
    @handle   = get_handle
    @marcxml  = get_marcxml
    @errors = {}
  end
  def valid?
    # assert MARCXML present
    # assert MARCXML file valid
    # assert handle file exists
    # assert handle file valid
    validate_path
    validate_handle
    validate_marcxml
    @errors.empty?
  end

  private

  def validate_path
    @errors[:path] << "bad path" unless File.readable?(@path)
  end

  def get_handle
    Handle.new(File.join(@path, 'handle'))
  end

  def get_marcxml
    wip_name = File.basename(@path)
    marcxml_paths = Dir.glob("#{File.join(@path, wip_name)}_marcxml.xml")
    raise "marcxml file count != 1" unless marcxml_paths.length == 1
    Marcxml.new(marcxml_paths[0])
  end
end
