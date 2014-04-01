#!/usr/bin/python

# Filename: aco_4_process_recs.py
# This Python script is used to:
#  1) for oclc records:
#		add a new 035 field containing the 001/003 BSN data from the original record using txt file
#		delete the 001/003 containing the OCLC number and add new 001/003 fields for the BSN data
#  2) for original records (lacking any OCLC record):
#		delete any existing 035 fields
#		copy the BSN data from the 001/003 fields to a new 035 field
#  3) for all records:
#		check record for presence of 880 script fields and write to .mrc files accordingly
#		check record for presence of RDA fields

import pymarc
from pymarc.field import Field
import codecs
import re

institution = raw_input("Enter the institution code (e.g., NNC for columbia, COO for cornell, NNU for nyu, or princeton): ")
batch_date = raw_input("Enter the date of the batch being processed in the format YYYYMMDD (e.g., 20140317):")
folder_name = institution + "_" + batch_date

rec_analysis_msgs = ''

# INPUT FILES
try:	marcRecsIn_oclc_recs_1 = pymarc.MARCReader(file(folder_name+'/'+folder_name+'_3_oclc_recs_1_batch.mrc'), to_unicode=True, force_utf8=True)
except: marcRecsIn_oclc_recs_1 = ''
try:	marcRecsIn_oclc_recs_2 = pymarc.MARCReader(file(folder_name+'/'+folder_name+'_3_oclc_recs_2_manual.mrc'), to_unicode=True, force_utf8=True)
except:	marcRecsIn_oclc_recs_2 = ''
try:	marcRecsIn_orig_recs_no_oclc = pymarc.MARCReader(file(folder_name+'/'+folder_name+'_3_orig_recs_no_oclc_nums.mrc'), to_unicode=True, force_utf8=True)
except:	marcRecsIn_orig_recs_no_oclc = ''
oclc_nums_bsns_txt = codecs.open(folder_name+'/'+folder_name+'_2_oclc_nums_bsns.txt', 'r', encoding='utf-8')	# opens the txt file containing the 001s, 003s, and corresponding OCLC nums (read-only)
oclc_nums_bsns_lines = oclc_nums_bsns_txt.readlines()	# read the txt file containing 001/003 and corresponding OCLC numbers

# OUTPUT FILES
marcRecsOut_recs_script = pymarc.MARCWriter(file(folder_name+'/'+folder_name+'_4_recs_script.mrc', 'w'))
marcRecsOut_recs_no_script = pymarc.MARCWriter(file(folder_name+'/'+folder_name+'_4_recs_no_script.mrc', 'w'))
rec_analysis_txt = codecs.open(folder_name+'/'+folder_name+'_4_rec_analysis.txt', 'w')

rec_count = 0				# variable to keep track of the total number of records processed
rec_count_file1 = 0			# variable to keep track of the number of records processed for File 1
rec_count_file2 = 0			# variable to keep track of the number of records processed for File 2
rec_count_file3 = 0			# variable to keep track of the number of records processed for File 3
rec_no_oclc_match_count = 0	# variable to keep track of the number of OCLC records that did not match an original record
recs_880s_count = 0			# variable to keep track of the number of records having 880 script fields
recs_no_880s_count = 0		# variable to keep track of the number of records NOT having 880 script fields
recs_rda_count = 0			# variable to keep track of the number of records having RDA 3XX or 040e fields

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
##  Method:  calculate_percentage()
######################################################################
def calculate_percentage(x,y):
	percentage = 100 * float(x)/float(y)
	percentage = round(percentage,1)
	return str(percentage)
	
######################################################################
##  Method:  process_record()
######################################################################
def process_record(rec):
	global rec_analysis_msgs
	rec_003_value = rec.get_fields('003')[0].value()	# the institutional code from the 003 (either "OCLC" or a partner institution)
	rec_001_value = rec.get_fields('001')[0].value()	# the local record number from the 001 (either the OCLC number or the partner's BSN)
	rec_analysis_msgs += 'Record '+rec_003_value+'_'+rec_001_value+'\n'
												
	if rec_001_value.startswith('o'):		# this is a record exported from oclc, not an original record
		# for oclc records, add a new 035 field and new 001/003 fields containing the orig record's 001/003 data using txt file
		# get list of OCLC numbers for this OCLC record from 035 subfields a and z
		rec_oclc_nums = set()
		if len(rec.get_fields('035')) > 0:					# check if there are any 035 fields in the OCLC record
			for rec_035 in rec.get_fields('035'):			# iterate through each of the 035 fields
				rec_035az = rec_035.get_subfields('a','z')	# capture all the subfields a or z in the 035 field
				if len(rec_035az) > 0:						# check if any subfields a or z exist
					for this_az in rec_035az:				# iterate through each of the subfields a or z
						this_oclc_num = strip_number(this_az)	# strip the subfield data down to just the OCLC number digits
						rec_oclc_nums.add(this_oclc_num)		# add the number to the list of this record's OCLC numbers
						rec_analysis_msgs += 'oclc_rec_035_num: '+str(this_az)+'\n'
		
		oclc_match = False
		for line in oclc_nums_bsns_lines:		# iterate through each of the lines in the txt file containing 001s/003s and OCLC numbers from original records
			if line.startswith('003'):			# this is the first header line in the txt file
				# skip the line
				skipped_line = line
			else:
				# process the line data from the txt file
				line_data = line.split(',')
				line_003 = line_data[0].strip()			# capture the partner's institution code
				line_001 = line_data[1].strip()			# capture the partner's bsn
				line_oclc_nums = line_data[2].strip()	# capture the corresponding OCLC numbers and remove any white space around them
				line_oclc_nums = line_oclc_nums.strip('"')	# remove the quotes around the OCLC number(s)
				line_oclc_nums = line_oclc_nums.split('|')	# create a list of the OCLC numbers based on the pipe delimiter, in case there are more than one

				for rec_oclc_num in rec_oclc_nums:
					for line_oclc_num in line_oclc_nums:
						if line_oclc_num == rec_oclc_num:
							oclc_match = True
							rec_analysis_msgs += 'Record matches: '+line_003+'_'+line_001+'\n'
							# add an 035 field to the OCLC record containing the 001/003 information from the original record
							line_bsn = '('+line_003+')'+line_001
							new_035_bsn = Field(tag='035', indicators=[' ',' '], subfields=['a',line_bsn])
							rec.add_field(new_035_bsn)
							
							# delete the existing 001/003 fields from the OCLC record containing the OCLC number and symbol
							rec.remove_field(rec.get_fields('003')[0])
							rec.remove_field(rec.get_fields('001')[0])
							
							# add new 001/003 fields to the OCLC record containing the partner's bsn and institution code
							new_003 = Field(tag='003', data=line_003)
							rec.add_field(new_003)
							new_001 = Field(tag='001', data=line_001)
							rec.add_field(new_001)
		if not oclc_match:
			rec_analysis_msgs += 'OCLC numbers did not match any original record\n'
			global rec_no_oclc_match_count
			rec_no_oclc_match_count +=1
			
	else:		# this is a partner's original record for which an OCLC record was not found in Connexion
		# for orig records, delete all existing 035 fields
		if len(rec_035s) > 0:
			for rec_035 in rec_035s:
				rec_analysis_msgs += 'orig_rec_035 num: '+str(rec_035)+'\n'
				rec.remove_field(rec_035)	# delete this 035 field
	
		# for orig records, copy the 001/003 BSN field data to an 035 field
		new_035_bsn = Field(tag='035', indicators=[' ',' '], subfields=['a','('+rec_003+')'+rec_001])
		rec.add_field(new_035_bsn)
			
	# check if record has 880 script fields and write to corresponding MARC record output file
	rec_880s = rec.get_fields('880')
	if len(rec_880s) > 0:
		marcRecsOut_recs_script.write(rec)
		global recs_880s_count
		recs_880s_count +=1
		rec_analysis_msgs += 'Record contains 880 script fields\n'
	else:
		marcRecsOut_recs_no_script.write(rec)
		global recs_no_880s_count
		recs_no_880s_count +=1
		rec_analysis_msgs += 'Record does NOT contain 880 script fields\n'
	
	# check if record uses RDA cataloging standards
	rec_336s = rec.get_fields('336')
	rec_337s = rec.get_fields('337')
	rec_338s = rec.get_fields('338')
	if len(rec.get_fields('040')[0].get_subfields('e')) > 0:
		rec_040e = rec.get_fields('040')[0].get_subfields('e')[0].value()
		rec_analysis_msgs += '040e field is '+rec_040e+'\n'
	else:
		rec_040e = ''
	if len(rec_336s)>0 or len(rec_337s)>0 or len(rec_338s)>0 or rec_040e=='rda':
		rec_analysis_msgs += 'Record contains RDA fields\n'
		global recs_rda_count
		recs_rda_count +=1
	
	rec_analysis_msgs += '-----------------------------------------------------------------\n'
	
######################################################################
##  MAIN SCRIPT
######################################################################
for record_oclc_1 in marcRecsIn_oclc_recs_1:
	process_record(record_oclc_1)
	rec_count +=1
	rec_count_file1 +=1

for record_oclc_2 in marcRecsIn_oclc_recs_2:
	process_record(record_oclc_2)
	rec_count +=1
	rec_count_file2 +=1

for record_orig in marcRecsIn_orig_recs_no_oclc:
	process_record(record_orig)
	rec_count +=1
	rec_count_file3 +=1

rec_analysis_msgs += 'Total records processed for '+folder_name+': '+str(rec_count)+' records\n'
rec_analysis_msgs += 'File 1 (oclc-batch): '+str(rec_count_file1)+'\n'
rec_analysis_msgs += 'File 2 (oclc-manual): '+str(rec_count_file2)+'\n'
rec_analysis_msgs += 'File 3 (orig-no oclc num): '+str(rec_count_file3)+'\n\n'

perc_880s = calculate_percentage(recs_880s_count,rec_count)
perc_no_880s = calculate_percentage(recs_no_880s_count,rec_count)
perc_rda = calculate_percentage(recs_rda_count,rec_count)
rec_analysis_msgs += 'Records where OCLC nums did not match: '+str(rec_no_oclc_match_count)+'\n'
rec_analysis_msgs += 'Records containing 880 script fields: '+str(recs_880s_count)+' ('+perc_880s+'%)\n'
rec_analysis_msgs += 'Records NOT containing 880 script fields: '+str(recs_no_880s_count)+' ('+perc_no_880s+'%)\n'
rec_analysis_msgs += 'Records containing RDA fields: '+str(recs_rda_count)+' ('+perc_rda+'%)\n'
rec_analysis_txt.write(rec_analysis_msgs)
print str(rec_count)+' records were processed in file'

oclc_nums_bsns_txt.close()
marcRecsOut_recs_script.close()
marcRecsOut_recs_no_script.close()
rec_analysis_txt.close()
