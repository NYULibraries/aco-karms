#!/usr/bin/python

import os
import errno
import sys
import time
import shutil
import codecs
import pymarc
from pymarc import Record, Field
from xml.dom.minidom import parseString
import aco_globals
import aco_functions

inst_code = raw_input('Enter the 3-letter institutional code: ')
batch_date = raw_input('Enter the batch date (YYYYMMDD): ')
batch_name = inst_code+'_'+batch_date
aco_globals.batch_folder += '/'+inst_code+'/'+batch_name

# Check if records have been processed before by this script
prev_processed = os.path.exists(aco_globals.batch_folder+'/'+batch_name+'_0_orig_recs.mrc')

if prev_processed:
	# Move previously processed ouput files to timestamped folder
	prev_file_timestamp = time.strftime('%Y%m%d_%H%M%S', time.gmtime(os.path.getmtime(aco_globals.batch_folder+'/'+batch_name+'_0_orig_recs.mrc')))
	dest_folder = aco_globals.batch_folder+'/'+batch_name+'_1_'+prev_file_timestamp+'/'
	try:
		os.makedirs(dest_folder)
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise
	src_folder = aco_globals.batch_folder+'/'
	src_0 = batch_name+'_0_orig_recs.mrc'
	src_1 = batch_name+'_1/'
	src_dirs = [src_0, src_1]
	for src in src_dirs:
		if os.path.exists(src_folder+src):
			shutil.move(src_folder+src, dest_folder+src)


# (Re)Process the records

# Convert the individual marcxml_in files to raw marc and write them all to a single .mrc file
# OUTPUT FILE
marcRecsOut_orig_recs = pymarc.MARCWriter(file(aco_globals.batch_folder+'/'+batch_name+'_0_orig_recs.mrc', 'w'))

marcxml_dir = aco_globals.batch_folder+'/marcxml_in'
for filename in os.listdir(marcxml_dir):
	file_path = os.path.join(marcxml_dir,filename)
	if os.path.isfile(file_path):
		if file_path[-3:]=='xml':
			marc_xml_array = pymarc.parse_xml_to_array(file_path)
			for rec in marc_xml_array:
				rec = aco_functions.pad_008(rec)
				marcRecsOut_orig_recs.write(rec)
marcRecsOut_orig_recs.close()

# Extract the OCLC numbers from each record and write records to .mrc and .txt files depending if record contains OCLC number or not
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

all_recs_analysis_txt = codecs.open(aco_globals.batch_folder+'/'+batch_name+'_1/'+batch_name+'_1_all_recs_analysis.txt', 'w', encoding='utf8')

######################################################################
##  MAIN SCRIPT
######################################################################
orig_rec_count_tot = 0		# variable to keep track of the total number of original records processed
orig_with_oclc_num_count = 0		# variable to keep track of the number of original records that have an OCLC number
orig_no_oclc_num_count = 0	# variable to keep track of the number of original records that do NOT have an OCLC number
batch_oclc_nums = set()	# set variable to capture unique list of OCLC numbers found in *all* records to be used for batch exporting from OCLC Connexion

orig_no_oclc_nums_txt.write('003/Inst,001/BSN,OCLC number(s),245a/Title\n')
orig_with_oclc_nums_txt.write('003/Inst,001/BSN,OCLC number(s),245a/Title\n')

for orig_rec in marcRecsIn_orig_recs:	# Iterate through all original records in marcRecsIn_orig_recs
	orig_003_value = orig_rec.get_fields('003')[0].value()	# the institutional code from the 003
	orig_001_value = orig_rec.get_fields('001')[0].value()	# the local BSN from the 001
	orig_245 = orig_rec.get_fields('245')[0]
	orig_245a = orig_245.get_subfields('a')[0]		# the main title from the 245 subfield a
	
	rec_oclc_nums = set()	# set variable to capture unique list of OCLC numbers for just this record
	oclc_num_exists = False
	for oclc_num_field in orig_rec.get_fields('035','079'):		# iterate through all the 035/079 fields in the original partner record
		oclc_num_field_az = oclc_num_field.get_subfields('a','z')	# capture the list of all subfields a or z in the 035/079 fields
		if len(oclc_num_field_az) > 0:								# check if subfield a or z exists in the 035/079 fields
			for this_az in oclc_num_field_az:						# iterate through each of the subfields a or z
				if this_az.startswith('(OCoLC)') or this_az.startswith('o'):	# check if the subfield data is an OCLC number
					this_oclc_num = aco_functions.strip_number(this_az)
					rec_oclc_nums.add(this_oclc_num)
					batch_oclc_nums.add(this_oclc_num)
					oclc_num_exists = True
	if oclc_num_exists:
		marcRecsOut_orig_with_oclc_nums.write(orig_rec)
		orig_with_oclc_nums_txt.write(orig_003_value+','+orig_001_value+',"')
		num_count = 0
		for num in rec_oclc_nums:
			orig_with_oclc_nums_txt.write(num)
			if num_count < len(rec_oclc_nums)-1:
				orig_with_oclc_nums_txt.write('|')
			num_count +=1
		orig_with_oclc_nums_txt.write('","'+orig_245a+'"\n')
		orig_with_oclc_num_count +=1
	else:
		marcRecsOut_orig_no_oclc_nums.write(orig_rec)
		orig_no_oclc_nums_txt.write(orig_003_value+','+orig_001_value+',,"'+orig_245a+'"\n')
		orig_no_oclc_num_count +=1
		
	orig_rec_count_tot +=1

for oclc_num in batch_oclc_nums:
	oclc_nums_for_export.write(oclc_num+'\n')

all_recs_analysis_txt.write('Total ORIGINAL records processed - batch '+batch_name+': '+str(orig_rec_count_tot)+' records\n')
all_recs_analysis_txt.write('Report produced: '+aco_globals.curr_time+'\n\n')
all_recs_analysis_txt.write('Orig records with OCLC number: '+str(orig_with_oclc_num_count)+'\n')
all_recs_analysis_txt.write('Orig records no OCLC number: '+str(orig_no_oclc_num_count)+'\n')
all_recs_analysis_txt.write('Total OCLC numbers for batch: '+str(len(batch_oclc_nums))+'\n')

print str(orig_rec_count_tot)+' records were processed in file'

marcRecsOut_orig_no_oclc_nums.close()
orig_no_oclc_nums_txt.close()
marcRecsOut_orig_with_oclc_nums.close()
orig_with_oclc_nums_txt.close()
oclc_nums_for_export.close()
all_recs_analysis_txt.close()
