class Handle
  attr_reader :handle, :prefix, :suffix
  def initialize(path)
    @path = path.dup
    @handle = @prefix = @suffix = nil
    process_path!
  end

  def to_url
    "http://hdl.handle.net/#{@handle}"
  end


  private
  def process_path!
    # check that handle file exists and is readable
    raise "handle file does not exist: #{@path}"  unless File.exists?(@path)
    raise "handle file is not readable: #{@path}" unless File.readable?(@path)

    # check that handle file only has one line
    lines = File.read(@path).split("\n")
    emsg = "handle file empty or has more than one line: #{@path}"
    raise emsg unless lines.length == 1
    handle = lines[0]

    # check handle format
    # ensure that there is only one '/' delimiter
    match = /\A([^\/]+)\/([^\/]+)\z/.match(handle)
    raise "incorrect handle format. expecting prefix/suffix"  if match.nil?
    @handle, @prefix, @suffix = match.to_a
  end
end
