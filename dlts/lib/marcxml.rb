require 'nokogiri'

class Marcxml
  def initialize(path)
    @path = path.dup
    @errors = {}
  end
end

