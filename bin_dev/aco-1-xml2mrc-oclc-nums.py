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

inst_code = raw_input('Enter the institutional code: ')
batch_date = raw_input('Enter the batch date (YYYYMMDD): ')
batch_name = inst_code+'_'+batch_date
aco_globals.batch_folder += '/'+inst_code+'/'+batch_name

# Check if records have been processed before by this script
prev_processed = os.path.exists(aco_globals.batch_folder+'/'+batch_name+'_0_orig_recs.mrc')

if prev_processed:
	# Move previously processed ouput files to timestamped folder
	prev_file_timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime(os.path.getmtime(aco_globals.batch_folder+'/'+batch_name+'_0_orig_recs.mrc')))
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

orig_rec_count_tot = 0			# variable to keep track of the total number of original records processed
orig_with_oclc_num_count = 0	# variable to keep track of the number of original records that have an OCLC number
orig_no_oclc_num_count = 0		# variable to keep track of the number of original records that do NOT have an OCLC number
batch_oclc_nums = set()			# set variable to capture unique list of OCLC numbers found in *all* records to be used for batch exporting from OCLC Connexion

# INPUT FILE(S)
# retrieve the CSV file containing the BSNs and source entity (SE) book numbers
try:
	bsn_se_csv = open(aco_globals.batch_folder+'/bsn-se-map.csv', 'r')
	aco_globals.bsn_se_lines = bsn_se_csv.readlines()
	bsn_se_csv.close()
except:	bsn_se_csv = ''

# OUTPUT FILES
try:
	os.makedirs(aco_globals.batch_folder+'/'+batch_name+'_1/')
except OSError as exception:
	if exception.errno != errno.EEXIST:
		raise

marcRecsOut_orig_no_oclc_nums = pymarc.MARCWriter(file(aco_globals.batch_folder+'/'+batch_name+'_1/'+batch_name+'_1_orig_no_oclc_nums.mrc', 'w'))
orig_no_oclc_nums_txt = codecs.open(aco_globals.batch_folder+'/'+batch_name+'_1/'+batch_name+'_1_orig_no_oclc_nums.txt', 'w', encoding='utf-8')
orig_no_oclc_nums_txt.write('003/Inst,001/BSN,OCLC number(s),245a/Title\n')

marcRecsOut_orig_with_oclc_nums = pymarc.MARCWriter(file(aco_globals.batch_folder+'/'+batch_name+'_1/'+batch_name+'_1_orig_with_oclc_nums.mrc', 'w'))
orig_with_oclc_nums_txt = codecs.open(aco_globals.batch_folder+'/'+batch_name+'_1/'+batch_name+'_1_orig_with_oclc_nums.txt', 'w', encoding='utf-8')
orig_with_oclc_nums_txt.write('003/Inst,001/BSN,OCLC number(s),245a/Title\n')

oclc_nums_for_export = codecs.open(aco_globals.batch_folder+'/'+batch_name+'_1/'+batch_name+'_1_oclc_nums_for_export.txt', 'w', encoding='utf-8')

all_recs_analysis_txt = codecs.open(aco_globals.batch_folder+'/'+batch_name+'_1/'+batch_name+'_1_all_recs_analysis.txt', 'w', encoding='utf8')

marcRecsOut_orig_recs = pymarc.MARCWriter(file(aco_globals.batch_folder+'/'+batch_name+'_0_orig_recs.mrc', 'w'))

# Convert the individual marcxml_in files to raw marc and write them all to a single .mrc file
marcxml_dir = aco_globals.batch_folder+'/marcxml_in'
for filename in os.listdir(marcxml_dir):
	file_path = os.path.join(marcxml_dir,filename)
	if os.path.isfile(file_path):
		if file_path[-3:]=='xml':
			marc_xml_array = pymarc.parse_xml_to_array(file_path)
			for orig_rec in marc_xml_array:
				orig_rec = aco_functions.pad_008(orig_rec)
				orig_003_value = orig_rec.get_fields('003')[0].value()	# the institutional code from the 003
				orig_001_value = orig_rec.get_fields('001')[0].value()	# the local BSN from the 001
				orig_245 = orig_rec.get_fields('245')[0]
				orig_245a = orig_245.get_subfields('a')[0]				# the main title from the 245 subfield a
				print orig_001_value
				orig_rec_count_tot +=1
				
				# Extract the OCLC numbers from each record and write records to .mrc and .txt files depending if record contains OCLC number or not
				rec_oclc_nums = set()	# set variable to capture unique list of OCLC numbers for just this record
				oclc_num_exists = False
				for oclc_num_field in rec.get_fields('035','079'):		# iterate through all the 035/079 fields in the original partner record
					oclc_num_field_az = oclc_num_field.get_subfields('a','z')	# capture the list of all subfields a or z in the 035/079 fields
					if len(oclc_num_field_az) > 0:								# check if subfield a or z exists in the 035/079 fields
						for this_az in oclc_num_field_az:						# iterate through each of the subfields a or z
							if this_az.startswith('(OCoLC)') or this_az.startswith('o'):	# check if the subfield data is an OCLC number
								this_oclc_num = aco_functions.strip_number(this_az)
								rec_oclc_nums.add(this_oclc_num)
								batch_oclc_nums.add(this_oclc_num)
								oclc_num_exists = True
				
				create_999_field(orig_rec, rec_oclc_nums)
				
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
				
				marcRecsOut_orig_recs.write(orig_rec)

marcRecsOut_orig_recs.close()



def create_999_field(rec, oclc_nums):
	rec_003 = rec.get_fields('003')[0].value()
	rec_001 = rec.get_fields('001')[0].value()
	
	rec_999s = rec.get_fields('999')
	if len(rec_999s) == 0:
		new_999 = Field(tag='999', indicators=[' ',' '], subfields=['i',rec_001])
		for oclc_num in oclc_nums:
			new_999.add_subfield('o',oclc_num)
		
		
		rec_orig.add_ordered_field(new_999)
		rec.add_ordered_field(new_999)
		msg += 'Record 999:  '+new_999.value()+'\n'
	elif len(rec_999s) > 0:
		msg += 'ERROR-MISC:  Record contains at least one 999 field\n'
		for rec_999 in rec_999s:
			msg += '   '+rec_999+'\n'



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
