require 'fileutils'

class WipProcessor

  # arguments: h
  # h = hash with the following key/value pairs
  #     h[:work_root] the root of the work directory tree, typically work/
  #     h[:wips]      an array of Wip objects to process
  def initialize(h)
    @work_root = File.expand_path(h[:work_root])
    @wips      = h[:wips]
    @date_str  = Time.now.strftime("%Y%m%d")

  end

  def run
    @wips.each do |w|
      process_wip(w)
    end
  end

  private
  def process_wip(w)
    str_003           = w.marcxml.get_003

    tgt_003_path      = File.join(@work_root, str_003)
    tgt_003_date_path = File.join(tgt_003_path, "#{str_003}_#{@date_str}")
    tgt_marcxml_path  = File.join(tgt_003_date_path, 'marcxml')
    csv_file_path     = File.join(tgt_003_date_path, 'handles.csv')

    # creates:
    #  tgt_003_path
    #  tgt_003_date_path
    #  tgt_marcxml_path
    FileUtils.mkdir_p(tgt_marcxml_path)
  end
end
