#!/usr/bin/python

import os
import pymarc
from pymarc import Record, Field
from xml.dom.minidom import parseString
import codecs

parent_dir = os.path.dirname(os.getcwd())
work_folder = parent_dir+'/work'
inst_code = raw_input('Enter the 3-letter institutional code: ')
batch_date = raw_input('Enter the batch date (YYYYMMDD): ')
batch_folder = work_folder+'/'+inst_code+'/'+inst_code+'_'+batch_date

marcRecsOut_orig_recs = pymarc.MARCWriter(file(batch_folder+'/'+inst_code+'_'+batch_date+'_1_orig_recs.mrc', 'w'))

marcxml_dir = batch_folder+'/marcxml_in'
for filename in os.listdir(marcxml_dir):
	file_path = os.path.join(marcxml_dir,filename)
	if os.path.isfile(file_path):
		if file_path[-3:]=='xml':
			marc_xml_array = pymarc.parse_xml_to_array(file_path)
			for rec in marc_xml_array:
				marcRecsOut_orig_recs.write(rec)
marcRecsOut_orig_recs.close()

# INPUT FILES
marcRecsIn_orig_recs = pymarc.MARCReader(file(batch_folder+'/'+inst_code+'_'+batch_date+'_1_orig_recs.mrc'), to_unicode=True, force_utf8=True)

# OUTPUT FILES
marcRecsOut_orig_recs_no_oclc_nums = pymarc.MARCWriter(file(batch_folder+'/'+inst_code+'_'+batch_date+'_2_orig_recs_no_oclc_nums.mrc', 'w'))
orig_recs_no_oclc_nums_txt = codecs.open(batch_folder+'/'+inst_code+'_'+batch_date+'_2_orig_recs_no_oclc_nums.txt', 'w', encoding='utf-8')
oclc_nums_batch_txt = codecs.open(batch_folder+'/'+inst_code+'_'+batch_date+'_2_oclc_nums_batch.txt', 'w', encoding='utf-8')
oclc_nums_bsns_batch_txt = open(batch_folder+'/'+inst_code+'_'+batch_date+'_2_oclc_nums_bsns_batch.txt', 'w')

######################################################################
##  Method:  strip_number()
######################################################################
def strip_number(oclc_subfield):
	import re
	digits_regex = re.compile('\d+')	# regular expression for matching a series of numerical characters only
	oclc_subfield = oclc_subfield.strip()							# remove any whitespace around the 035 a/z content
	oclc_subfield_digits = re.findall(digits_regex,oclc_subfield)	# extract just the OCLC number from the 035 a/z
	oclc_subfield_digits = oclc_subfield_digits[0].lstrip('0')		# remove any leading zeros from the OCLC number
	return oclc_subfield_digits

######################################################################
##  MAIN SCRIPT
######################################################################
rec_count_tot = 0		# variable to keep track of the total number of original records processed
oclc_num_count = 0		# variable to keep track of the number of original records that have an OCLC number
no_oclc_num_count = 0	# variable to keep track of the number of original records that do NOT have an OCLC number
batch_oclc_nums = set()	# set variable to capture unique list of OCLC numbers found in *all* records to be used for batch exporting from OCLC Connexion

orig_recs_no_oclc_nums_txt.write('003/Inst,001/BSN,OCLC number(s),245a/Title\n')
oclc_nums_bsns_batch_txt.write('003/Inst,001/BSN,OCLC number(s)\n')

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
					this_oclc_num = strip_number(this_az)
					rec_oclc_nums.add(this_oclc_num)
					batch_oclc_nums.add(this_oclc_num)
					oclc_num_exists = True
					oclc_num_count +=1
	if oclc_num_exists:
		oclc_nums_bsns_batch_txt.write(orig_003_value+','+orig_001_value+',"')
		num_count = 0
		for num in rec_oclc_nums:
			oclc_nums_bsns_batch_txt.write(num)
			if num_count < len(rec_oclc_nums)-1:
				oclc_nums_bsns_batch_txt.write('|')
			num_count +=1
		oclc_nums_bsns_batch_txt.write('"\n')
	else:
		marcRecsOut_orig_recs_no_oclc_nums.write(record_orig)
		orig_recs_no_oclc_nums_txt.write(orig_003_value+','+orig_001_value+',,"'+orig_245a+'"\n')
		no_oclc_num_count +=1
			
	rec_count_tot +=1

for oclc_num in batch_oclc_nums:
	oclc_nums_batch_txt.write(oclc_num+'\n')
print str(rec_count_tot)+' records were processed in file'

marcRecsOut_orig_recs_no_oclc_nums.close()
orig_recs_no_oclc_nums_txt.close()
oclc_nums_batch_txt.close()
oclc_nums_bsns_batch_txt.close()
