#!/usr/bin/python

import os
import errno
import pymarc
from pymarc import Record, Field
from xml.dom.minidom import parseString
import codecs
import time
import shutil
import aco_globals
import aco_functions

inst_code = raw_input('Enter the 3-letter institutional code: ')
batch_date = raw_input('Enter the batch date (YYYYMMDD): ')
batch_name = inst_code+'_'+batch_date
aco_globals.batch_folder += '/'+inst_code+'/'+batch_name

# check if this batch has been run as NEW before, and if so, move the output files for the first run into a separate folder
new_output_folder = aco_globals.batch_folder+'/'+batch_name+'_3_new'
new_exists = os.path.exists(new_output_folder+'/'+batch_name+'_6_final_recs.mrc')
if new_exists:
	# get timestamp of the file above
	new_file_timestamp = time.strftime('%Y%m%d_%H%M%S', time.gmtime(os.path.getmtime(new_output_folder+'/'+batch_name+'_6_final_recs.mrc')))
	print new_file_timestamp
	dest_folder = aco_globals.batch_folder+'/'+batch_name+'_process_new_'+new_file_timestamp+'/'
	src_folder = aco_globals.batch_folder+'/'
	src_marcxml_out = 'marcxml_out/'
	src_mrc_out = 'mrc_out/'
	src_0 = batch_name+'_0_orig_recs.mrc'
	src_1 = batch_name+'_1/'
	src_2 = batch_name+'_2_oclc_recs_batch.mrc'
	src_3 = batch_name+'_3_new/'
	src_6 = batch_name+'_6_final_recs.mrc'
	src_dirs = (src_marcxml_out, src_mrc_out, src_0, src_1, src_2, src_3, src_6)
	# move related process-new output files from previous run into a separate folder labeled with the processing timestamp
	for src in src_dirs:
		if os.path.exists(src_folder+src):
			shutil.move(src_folder+src, dest_folder+src)

# OUTPUT FILE
marcRecsOut_orig_recs = pymarc.MARCWriter(file(aco_globals.batch_folder+'/'+batch_name+'_0_orig_recs.mrc', 'w'))

marcxml_dir = aco_globals.batch_folder+'/marcxml_in'
for filename in os.listdir(marcxml_dir):
	file_path = os.path.join(marcxml_dir,filename)
	if os.path.isfile(file_path):
		if file_path[-3:]=='xml':
			marc_xml_array = pymarc.parse_xml_to_array(file_path)
			for rec in marc_xml_array:
				marcRecsOut_orig_recs.write(rec)
marcRecsOut_orig_recs.close()

# INPUT FILE
marcRecsIn_orig_recs = pymarc.MARCReader(file(aco_globals.batch_folder+'/'+batch_name+'_0_orig_recs.mrc'), to_unicode=True, force_utf8=True)

# OUTPUT FILES
try:
	os.makedirs(aco_globals.batch_folder+'/'+batch_name+'_1/')
except OSError as exception:
	if exception.errno != errno.EEXIST:
		raise

marcRecsOut_orig_no_oclc_nums = pymarc.MARCWriter(file(aco_globals.batch_folder+'/'+batch_name+'_1/'+batch_name+'_1_orig_no_oclc_nums.mrc', 'w'))
orig_no_oclc_nums_txt = codecs.open(aco_globals.batch_folder+'/'+batch_name+'_1/'+batch_name+'_1_orig_no_oclc_nums.txt', 'w', encoding='utf-8')

marcRecsOut_orig_with_oclc_nums = pymarc.MARCWriter(file(aco_globals.batch_folder+'/'+batch_name+'_1/'+batch_name+'_1_orig_with_oclc_nums.mrc', 'w'))
orig_with_oclc_nums_txt = codecs.open(aco_globals.batch_folder+'/'+batch_name+'_1/'+batch_name+'_1_orig_with_oclc_nums.txt', 'w', encoding='utf-8')

oclc_nums_for_export = codecs.open(aco_globals.batch_folder+'/'+batch_name+'_1/'+batch_name+'_1_oclc_nums_for_export.txt', 'w', encoding='utf-8')

######################################################################
##  MAIN SCRIPT
######################################################################
rec_count_tot = 0		# variable to keep track of the total number of original records processed
oclc_num_count = 0		# variable to keep track of the number of original records that have an OCLC number
no_oclc_num_count = 0	# variable to keep track of the number of original records that do NOT have an OCLC number
batch_oclc_nums = set()	# set variable to capture unique list of OCLC numbers found in *all* records to be used for batch exporting from OCLC Connexion

orig_no_oclc_nums_txt.write('003/Inst,001/BSN,OCLC number(s),245a/Title\n')
orig_with_oclc_nums_txt.write('003/Inst,001/BSN,OCLC number(s),245a/Title\n')

for record_orig in marcRecsIn_orig_recs:	# Iterate through all original records in marcRecsIn_orig_recs
	orig_003_value = record_orig.get_fields('003')[0].value()	# the institutional code from the 003
	orig_001_value = record_orig.get_fields('001')[0].value()	# the local BSN from the 001
	orig_245 = record_orig.get_fields('245')[0]
	orig_245a = orig_245.get_subfields('a')[0]		# the main title from the 245 subfield a
	
	rec_oclc_nums = set()	# set variable to capture unique list of OCLC numbers for just this record
	oclc_num_exists = False
	for oclc_num_field in record_orig.get_fields('035','079'):		# iterate through all the 035/079 fields in the original partner record
		oclc_num_field_az = oclc_num_field.get_subfields('a','z')	# capture the list of all subfields a or z in the 035/079 fields
		if len(oclc_num_field_az) > 0:								# check if subfield a or z exists in the 035/079 fields
			for this_az in oclc_num_field_az:						# iterate through each of the subfields a or z
				if this_az.startswith('(OCoLC)') or this_az.startswith('o'):	# check if the subfield data is an OCLC number
					this_oclc_num = aco_functions.strip_number(this_az)
					rec_oclc_nums.add(this_oclc_num)
					batch_oclc_nums.add(this_oclc_num)
					oclc_num_exists = True
					oclc_num_count +=1
	if oclc_num_exists:
		marcRecsOut_orig_with_oclc_nums.write(record_orig)
		orig_with_oclc_nums_txt.write(orig_003_value+','+orig_001_value+',"')
		num_count = 0
		for num in rec_oclc_nums:
			orig_with_oclc_nums_txt.write(num)
			if num_count < len(rec_oclc_nums)-1:
				orig_with_oclc_nums_txt.write('|')
			num_count +=1
		orig_with_oclc_nums_txt.write('","'+orig_245a+'"\n')
	else:
		marcRecsOut_orig_no_oclc_nums.write(record_orig)
		orig_no_oclc_nums_txt.write(orig_003_value+','+orig_001_value+',,"'+orig_245a+'"\n')
		no_oclc_num_count +=1
		
	rec_count_tot +=1

for oclc_num in batch_oclc_nums:
	oclc_nums_for_export.write(oclc_num+'\n')
print str(rec_count_tot)+' records were processed in file'

marcRecsOut_orig_no_oclc_nums.close()
orig_no_oclc_nums_txt.close()
marcRecsOut_orig_with_oclc_nums.close()
orig_with_oclc_nums_txt.close()
oclc_nums_for_export.close()
