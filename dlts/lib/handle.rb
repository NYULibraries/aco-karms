class Handle
  attr_reader :handle, :prefix, :suffix
  def initialize(path)
    @path = path.dup
    @errors = {}
    @handle = @prefix = @suffix = nil
    process_path!
  end

  private
  def process_path!
    # check that handle file exists and is readable
    raise "handle file does not exist"   unless File.exists?(@path)
    raise "handle file must be readable" unless File.readable?(@path)

    # check that handle file only has one line
    lines = File.read(@path).split("\n")
    raise "handle file empty or has more than one line"  unless lines.length == 1
    handle = lines[0]

    # check handle format
    # ensure that there is only one '/' delimiter
    match = /\A([^\/]+)\/([^\/]+)\z/.match(handle)
    raise "incorrect handle format. expecting prefix/suffix"  if match.nil?
    @handle, @prefix, @suffix = match
  end
end

