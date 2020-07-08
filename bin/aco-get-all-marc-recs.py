#!/usr/bin/python

import os
import errno
import sys
import time
import shutil
import codecs
import pymarc
from pymarc import Record, Field
import aco_globals
import aco_functions

def wrapper(gen):
  while True:
    try:
      yield next(gen)
    except StopIteration:
      break
    except Exception as e:
      print(e) # or whatever kind of logging you want


aco_mrc_all = pymarc.MARCWriter(file(aco_globals.work_folder+'/'+'mrc_out_all-3.mrc', 'w'))

# Retrieve individual final MARC files from each mrc_out batch folder
for root, folders, files in os.walk(aco_globals.work_folder):
	for folder in folders:
		if folder == "mrc_out":
			mrc_out_path = os.path.join(root, folder)
			for root, folders, files in os.walk(mrc_out_path):
				for mrc_file in files:
					mrc_file_path = os.path.join(root, mrc_file)
					this_mrc_files = pymarc.MARCReader(file(mrc_file_path), to_unicode=True, force_utf8=True)
					for this_mrc_file in list(wrapper(this_mrc_files)):
						this_mrc_003 = this_mrc_file.get_fields('003')[0].value()
						this_mrc_001 = this_mrc_file.get_fields('001')[0].value()
						print '('+this_mrc_003+')'+this_mrc_001
						aco_mrc_all.write(this_mrc_file)

