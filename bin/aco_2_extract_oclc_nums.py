#!/usr/bin/python

# Filename: aco_2_extract_oclc_nums.py
# This Python script is used to:
# 1)  extract the unique OCLC numbers from the original ACO MARC records
# 2)  write the list of all OCLC numbers to two .txt files:
#     -  one file containing *just* the OCLC numbers to be used for batch processing in Connexion (2_oclc_nums_for_batch.txt) and
#     -  one file containing the 001s (institution codes), 003s (BSNs), and OCLC numbers to be used for reference (2_oclc_nums_bsns.txt)
# 3)  write the original records lacking an OCLC number to an .mrc file (2_no_oclc_nums_recs.mrc)
# 4)  write the list of 001 and 003 fields for original records lacking an OCLC number to a txt file for reference (2_no_oclc_nums_bsns.txt)

import pymarc
from pymarc.field import Field
import codecs
import re

institution = raw_input("Enter the institution code (e.g., NNC for columbia, COO for cornell, NNU for nyu, or princeton): ")
batch_date = raw_input("Enter the date of the batch being processed in the format YYYYMMDD (e.g., 20140317):")
folder_name = institution + "_" + batch_date

# INPUT FILES
marcRecsIn_orig_recs = pymarc.MARCReader(file(folder_name+'/'+folder_name+'_1_orig_recs.mrc'), to_unicode=True, force_utf8=True)

# OUTPUT FILES
marcRecsOut_orig_recs_no_oclc_nums = pymarc.MARCWriter(file(folder_name+'/'+folder_name+'_2_orig_recs_no_oclc_nums.mrc', 'w'))
orig_recs_no_oclc_nums_txt = codecs.open(folder_name+'/'+folder_name+'_2_orig_recs_no_oclc_nums.txt', 'w', encoding='utf-8')
oclc_nums_for_batch_txt = codecs.open(folder_name+'/'+folder_name+'_2_oclc_nums_for_batch.txt', 'w', encoding='utf-8')
oclc_nums_bsns_txt = codecs.open(folder_name+'/'+folder_name+'_2_oclc_nums_bsns.txt', 'w', encoding='utf-8')

######################################################################
##  Method:  strip_number()
######################################################################
def strip_number(oclc_subfield):
	digits_regex = re.compile('\d+')	# regular expression for matching a series of numerical characters only
	oclc_subfield = oclc_subfield.strip()							# remove any whitespace around the 035 a/z content
	oclc_subfield_digits = re.findall(digits_regex,oclc_subfield)	# extract just the OCLC number from the 035 a/z
	oclc_subfield_digits = oclc_subfield_digits[0].lstrip('0')		# remove any leading zeros from the OCLC number
	return oclc_subfield_digits

######################################################################
##  MAIN SCRIPT
######################################################################
rec_count = 0			# variable to keep track of the total number of original records processed
oclc_num_count = 0		# variable to keep track of the number of original records that have an OCLC number
no_oclc_num_count = 0	# variable to keep track of the number of original records that do NOT have an OCLC number
batch_oclc_nums = set()		# set variable to capture unique list of OCLC numbers found in *all* records to be used for batch exporting from OCLC Connexion

orig_recs_no_oclc_nums_txt.write('003/Inst,001/BSN,OCLC number(s),245a/Title\n')
oclc_nums_bsns_txt.write('003/Inst,001/BSN,OCLC number(s),245a/Title\n')

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
		oclc_nums_bsns_txt.write(orig_003_value+','+orig_001_value+',"')
		num_count = 0
		for num in rec_oclc_nums:
			oclc_nums_bsns_txt.write(num)
			if num_count < len(rec_oclc_nums)-1:
				oclc_nums_bsns_txt.write('|')
			num_count +=1
		oclc_nums_bsns_txt.write('","'+orig_245a+'"\n')
	else:
		marcRecsOut_orig_recs_no_oclc_nums.write(record)
		orig_recs_no_oclc_nums_txt.write(orig_003_value+','+orig_001_value+',,"'+orig_245a+'"\n')
		no_oclc_num_count +=1
			
	rec_count +=1

for oclc_num in batch_oclc_nums:
	oclc_nums_for_batch_txt.write(oclc_num+'\n')
print str(rec_count)+' records were processed in file'

marcRecsOut_orig_recs_no_oclc_nums.close()
orig_recs_no_oclc_nums_txt.close()
oclc_nums_for_batch_txt.close()
oclc_nums_bsns_txt.close()
