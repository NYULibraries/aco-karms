require 'nokogiri'

class Handle
  def initialize(path)
    @path = path.dup
    @errors = {}
  end
end

