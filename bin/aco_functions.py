import os
import errno
import pymarc
from pymarc import Record, Field
import codecs
import re
import datetime
import string
from copy import deepcopy
import aco_globals
import xml.dom.minidom

######################################################################
##  Method:  pad_008() - for NYU records, pads the 008 field to 40 chars
##		fixing when blanks in bytes 38 and/or 39 are deleted when
##		exported out of Aleph using URL template
######################################################################
def pad_008(rec):
	rec_008_val = rec.get_fields('008')[0].value()
	if len(rec_008_val) < 40:
		pad_008_val = rec_008_val.ljust(40)
		
		# delete the existing 008 field from the original record
		rec.remove_field(rec.get_fields('008')[0])
		
		# add new 008 field padded to 40 chars to the original record
		new_008 = Field(tag='008', data=pad_008_val)
		rec.add_ordered_field(new_008)
		
	return rec
		

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
##  Method:  process_001_003_fields()
##  -  For OCLC records:
##     -  extract OCLC numbers from 035 field, subfields $a and $z of OCLC record
##     -  match OCLC num from OCLC record with list in .txt file to capture corresponding BSN information from original record
##     -  delete existing 003/001 fields containing the OCLC number
##     -  add 003/001 fields with institutional code and BSN from original record
##  -  For original records with no OCLC record:
##     -  delete all existing 035 fields
##  -  add 999 $i for institutional BSN info and $o for OCLC number
######################################################################
def process_001_003_fields(rec_orig, rec, oclc_nums_bsns_all):
	msg = ''
	oclc_id = ''
	inst_id = ''
	oclc_match = False
	rec_003_value = rec.get_fields('003')[0].value()	# the institutional code from the 003 (either "OCLC" or a partner institution)
	rec_001_value = rec.get_fields('001')[0].value()	# the local record number from the 001 (either the OCLC number or the partner's BSN)
	
	# Process OCLC records exported from Connexion
	if rec_001_value.startswith('o'):
		oclc_id = '('+rec_003_value+')'+rec_001_value
		msg += 'OCLC ID: '+oclc_id+'\n'
		
		# for oclc records, add a new 999 $i subfield containing the orig record's 001/003 data using txt file
		# extract list of OCLC numbers for this OCLC record from 035 subfields $a and $z
		rec_oclc_nums = set()
		if len(rec.get_fields('035')) > 0:					# check if there are any 035 fields in the OCLC record
			for rec_035 in rec.get_fields('035'):			# iterate through each of the 035 fields
				rec_035az = rec_035.get_subfields('a','z')	# capture all the subfields a or z in the 035 field
				if len(rec_035az) > 0:						# check if any subfields a or z exist
					for this_az in rec_035az:				# iterate through each of the subfields a or z
						this_oclc_num = strip_number(this_az)	# strip the subfield data down to just the OCLC number digits
						rec_oclc_nums.add(this_oclc_num)		# add the number to the list of this record's OCLC numbers
						msg += '   oclc_rec_035_num: '+str(this_az)+'\n'
		
		for line in oclc_nums_bsns_all:		# iterate through each of the lines in the txt file containing 001s/003s and OCLC numbers from original records
			if line.startswith('003'):		# this is the first header line in the txt file
				# skip the header row
				skipped_line = line
			else:
				# process the line data from the oclc_nums_bsns_all txt file
				line_data = line.split(',')
				line_003 = line_data[0].strip()			# capture the partner's institution code
				line_001 = line_data[1].strip()			# capture the partner's bsn
				line_oclc_nums = line_data[2].strip()	# capture the corresponding OCLC numbers and remove any white space around them
				line_oclc_nums = line_oclc_nums.strip('"')	# remove the quotes around the OCLC number(s)
				line_oclc_nums = line_oclc_nums.split('|')	# create a list of the OCLC numbers based on the pipe delimiter, in case there are more than one
				
				# iterate through this record's OCLC numbers to see if one is in the list of all OCLC numbers for this batch
				for rec_oclc_num in rec_oclc_nums:
					for line_oclc_num in line_oclc_nums:
						if line_oclc_num == rec_oclc_num:
							oclc_match = True
							inst_id = line_003+'_'+line_001
							msg += 'Institution ID: '+inst_id+'\n'
							
							# delete the existing 001/003 fields from the OCLC record containing the OCLC number and symbol
							rec.remove_field(rec.get_fields('003')[0])
							rec.remove_field(rec.get_fields('001')[0])
							
							# add new 001/003 fields to the OCLC record containing the partner's bsn and institution code
							new_003 = Field(tag='003', data=line_003)
							rec.add_ordered_field(new_003)
							new_001 = Field(tag='001', data=line_001)
							rec.add_ordered_field(new_001)
		if not oclc_match:
			msg += 'ERROR-MISC:  OCLC numbers in this OCLC record did not match any original record\n'
	
	# Process Original Records (no OCLC record found in Connexion)
	else:
		inst_id = rec_003_value+'_'+rec_001_value
		msg += 'Institution ID: '+inst_id+'\n'
		
		# for orig records, delete all existing 035 fields
		if len(rec.get_fields('035')) > 0:
			for rec_035 in rec.get_fields('035'):
				msg += '   orig_rec_035 num: '+str(rec_035)+'\n'
				rec.remove_field(rec_035)	# delete this 035 field
	
	rec_999s = rec.get_fields('999')
	if len(rec_999s) == 0:
		if oclc_id == '':
			new_999_nums = Field(tag='999', indicators=[' ',' '], subfields=['i',inst_id])
		else:
			new_999_nums = Field(tag='999', indicators=[' ',' '], subfields=['i',inst_id,'o',oclc_id])
		rec_orig.add_ordered_field(new_999_nums)
		rec.add_ordered_field(new_999_nums)
		msg += 'Record 999:  '+new_999_nums.value()+'\n'
	elif len(rec_999s) > 1:
		msg += 'ERROR-MISC:  Record contains multiple 999 fields\n'
		for rec_999 in rec_999s:
			msg += '   '+rec_999+'\n'
	elif len(rec_999s) == 1:
		new_999 = deepcopy(rec_999s[0])
		for new_999e in new_999.get_subfields('e'):
			# delete any existing subfield $e in the new 999 field
			new_999.delete_subfield('e')
		msg += 'Record 999:  '+new_999.value()+'\n'
	
	return (rec_orig, rec, oclc_id, inst_id, oclc_match, msg)

######################################################################
##  Method:  check_for_missing_880s()
##  -  check if record is missing 880 script fields
######################################################################
def check_for_missing_880s(rec):
	msg = ''
	script_rec = True
	missing_key_880s = False
	rec_880s = rec.get_fields('880')
	if len(rec_880s) == 0:			# the record does not contain *any* 880 script fields
		script_rec = False
		msg += 'ERROR-880: 880 script fields: NO\n'
	else:
		msg += '880 script fields: YES\n'
		missing_key_880s, msg_b = check_for_key_script_fields(rec)
		if missing_key_880s:		# the record contains 880s but some key fields are missing 880s
			msg += msg_b
	
	return (script_rec, missing_key_880s, msg)

######################################################################
##  Method:  check_for_key_script_fields()
##  -  check for any key MARC fields lacking 880 script fields - i.e., does not have subfield $6
######################################################################
def check_for_key_script_fields(rec):
	msg = 'ERROR-880: Key fields missing script 880 field (i.e., missing subfield $6):\n'
	missing_key_880s = False
	rec_key_fields = rec.get_fields('100','110','111','130','240','245','246','250','260','264','440','490','700','710','711','730','800','810','811','830')
	for rec_key_field in rec_key_fields:
		rec_key_field_6s = rec_key_field.get_subfields('6')
		if len(rec_key_field_6s) == 0:
			missing_key_880s = True
			msg += '   '+rec_key_field.tag+' - '+rec_key_field.value()+'\n'

	return (missing_key_880s, msg)
			
######################################################################
##  Method:  check_for_unlinked_880s()
##  -  check if record has any UNLINKED 880 fields (i.e., has "-00" in subfield $6)
######################################################################
def check_for_unlinked_880s(rec):
	msg = ''
	msg_unlnkd_880_6s = ''
	rec_003_value = rec.get_fields('003')[0].value()
	rec_001_value = rec.get_fields('001')[0].value()
	
	# get lists of 880s that are unlinked and separate those that have a single parallel field and need sequenced
	# from those that either don't have a parallel field or have more than one parallel field and do NOT get sequenced
	unlinked_880s_exist = False
	rec_880s = rec.get_fields('880')
	for rec_880 in rec_880s:
		rec_880_6s = rec_880.get_subfields('6')
		if len(rec_880_6s)==0 or len(rec_880_6s) > 1:
			msg += 'ERROR-MISC: There are either zero or multiple subfield $6s in this 880: '+rec_880+'\n'
		else:
			rec_880_6 = rec_880_6s[0]
			if rec_880_6[4:6]=='00':
				unlinked_880s_exist = True
				msg_unlnkd_880_6s += '   880 $6 '+rec_880_6+' - '
				rec_880_pf = rec_880_6[0:3]				# get the corresponding parallel MARC field tag
				rec_pfs = rec.get_fields(rec_880_pf)
				if len(rec_pfs) == 0:					# a parallel field does NOT exist, so don't sequence this 880
					msg_unlnkd_880_6s += 'A parallel field does NOT exist for this unlinked 880 - NEED TO CREATE PF\n'
				elif len(rec_pfs) > 1:					# there is MORE THAN ONE parallel field, so don't sequence this 880
					msg_unlnkd_880_6s += 'There are multiple parallel fields for this unlinked 880 - NEED TO DISTIINGUISH PF\n'
				else:									# only ONE parallel field DOES exist, so this 880 needs sequenced
					msg_unlnkd_880_6s += 'There is one parallel field for this unlinked 880 - NEED TO CHECK PF\n'
	
	if unlinked_880s_exist:
		msg += 'ERROR-880: Unlinked 880s: YES\n'
		msg += msg_unlnkd_880_6s
	
	return (unlinked_880s_exist, msg)

######################################################################
##  Method:  link_880s() - OLD FUNCTION which tries to link unlinked 880s
######################################################################
# def link_880s_old(rec):
# 	msg = ''
# 	msg_unlnkd_880_6s = ''
# 	rec_003_value = rec.get_fields('003')[0].value()
# 	rec_001_value = rec.get_fields('001')[0].value()
# 	rec_880s = rec.get_fields('880')
# 	
# 	# get lists of 880s that are unlinked and separate those that have a single parallel field and need sequenced
# 	# from those that either don't have a parallel field or have more than one parallel field and do NOT get sequenced
# 	unlinked_880s_exist = False
# 	rec_880s_to_seq = []
# 	rec_880s_dont_seq = []
# 	for rec_880 in rec_880s:
# 		rec_880_6s = rec_880.get_subfields('6')
# 		if len(rec_880_6s)==0 or len(rec_880_6s) > 1:
# 			msg += 'ERROR-MISC: There are either zero or multiple subfield $6s in this 880: '+rec_880+'\n'
# 			for rec_880_6 in rec_880_6s:
# 				rec_880s_dont_seq.append(rec_880_6)
# 		else:
# 			rec_880_6 = rec_880_6s[0]
# 			if rec_880_6[4:6]=='00':
# 				unlinked_880s_exist = True
# 				msg_unlnkd_880_6s += '   880 $6 '+rec_880_6+' - '
# 				rec_880_pf = rec_880_6[0:3]				# get the corresponding parallel MARC field tag
# 				rec_pfs = rec.get_fields(rec_880_pf)
# 				if len(rec_pfs) == 0:					# a parallel field does NOT exist, so don't sequence this 880
# 					rec_880s_dont_seq.append(rec_880_6)
# 					msg_unlnkd_880_6s += 'A parallel field does NOT exist for this unlinked 880: '+rec_880_6+'\n'
# 				elif len(rec_pfs) > 1:					# there is MORE THAN ONE parallel field, so don't sequence this 880
# 					rec_880s_dont_seq.append(rec_880_6)
# 					msg_unlnkd_880_6s += 'There are multiple parallel fields for this unlinked 880: '+rec_880_6+'\n'
# 				else:									# only ONE parallel field DOES exist, so this 880 needs sequenced
# 					rec_880s_to_seq.append(rec_880_6)
# 	
# 	if unlinked_880s_exist:
# 		msg += 'ERROR-880: Unlinked 880s: YES\n'
# 		msg += msg_unlnkd_880_6s
# 	
# 	# run through the 880 fields again and re-sequence any unlinked 880s that DO have a single parallel field in the record
# 	if unlinked_880s_exist and len(rec_880s_to_seq) > 0:
# 		seq_i = 1					# variable to keep track of the new 880 sequence number
# 		for rec_880 in rec_880s:
# 			unlnkd_880 = False		# variable to keep track of whether this 880 is unlinked
# 			seq_880 = True			# variable to keep track of whether this 880 needs re-sequenced
# 			seq_i_str = str(seq_i).zfill(2)		# add a leading zero to the sequence number if it's only one digit
# 			rec_880_6 = rec_880.get_subfields('6')[0]	# to get to this point, there will only be a single subfield $6
# 			if rec_880_6[4:6] == '00':
# 				for rec_880_dont_seq in rec_880s_dont_seq:
# 					if rec_880_6 == rec_880_dont_seq:
# 						seq_880 = False		# the 880 is unlinked but needs to be manually reviewed (i.e., do not re-sequence)
# 			if seq_880:
# 				rec_880_ind1 = rec_880.indicator1
# 				rec_880_ind2 = rec_880.indicator2
# 				new_rec_880 = Field(tag='880', indicators=[rec_880_ind1,rec_880_ind2], subfields=[])
# 				new_rec_880_6 = rec_880_6[0:3]+'-'+seq_i_str+'/r'
# 				new_rec_880.add_subfield('6',new_rec_880_6)
# 				rec_880.delete_subfield('6')
# 				for rec_880_sub in rec_880:
# 					new_rec_880.add_subfield(rec_880_sub[0],rec_880_sub[1])
# 				rec.remove_field(rec_880)
# 				rec.add_ordered_field(new_rec_880)
# 				seq_i += 1
# 		
# 		# retrieve new/updated set of 880 fields in the record, then re-sequence the parallel fields to match the new 880 sequence numbers
# 		upd_rec_880s = rec.get_fields('880')
# 		for upd_rec_880 in upd_rec_880s:
# 			upd_rec_880_6s = upd_rec_880.get_subfields('6')
# 			if len(upd_rec_880_6s)==1:
# 				upd_rec_880_6 = upd_rec_880_6s[0]
# 				if not upd_rec_880_6[4:6] == '00':
# 					upd_rec_880_seq_num = upd_rec_880_6[4:6]
# 					rec_880_pf = upd_rec_880_6[0:3]
# 					rec_pfs = rec.get_fields(rec_880_pf)
# 					
# 					if len(rec_pfs) == 1:
# 						rec_pf = rec_pfs[0]
# 						rec_pf_ind1 = rec_pf.indicator1
# 						rec_pf_ind2 = rec_pf.indicator2
# 						
# 						
# 						# add new parallel field with new sequence numbering in the subfield $6
# 						new_rec_pf = Field(tag=rec_880_pf, indicators=[rec_pf_ind1,rec_pf_ind2], subfields=[])
# 						new_rec_pf_6 = '880-'+upd_rec_880_seq_num
# 						new_rec_pf.add_subfield('6',new_rec_pf_6)
# 						
# 						# delete the subfield $6s from the existing parallel field
# 						rec_pf_6s = rec_pf.get_subfields('6')
# 						for rec_pf_6 in rec_pf_6s:
# 							rec_pf.delete_subfield('6')
# 						# add the remaining subfields from the existing parallel field into the new parallel field
# 						for rec_pf_sub in rec_pf:
# 							new_rec_pf.add_subfield(rec_pf_sub[0],rec_pf_sub[1])
# 						# delete the existing parallel field
# 						rec.remove_field(rec_pf)
# 						# add the new parallel field
# 						rec.add_ordered_field(new_rec_pf)
# 	
# 	return (rec, unlinked_880s_exist, msg)

######################################################################
##  Method:  check_series_hdgs()
##  -  check if record has corresponding 800/810/811/830 fields for any 490 series fields
######################################################################
def check_series_hdgs(rec):
	msg = ''
	rec_490s = rec.get_fields('490')
	rec_8XXs = rec.get_fields('800','810','811','830')
	if len(rec_490s) > len(rec_8XXs):
		msg += 'ERROR-SERIES: There are 490 fields that are missing a corresponding 8XX field\n'
	for rec_490 in rec_490s:
		rec_490_ind1 = rec_490.indicator1
		if rec_490_ind1 == '0':
			msg += 'ERROR-SERIES: This 490 field needs traced (1st indicator is 0): '+rec_490.value()+'\n'
	return (msg)
	
######################################################################
##  Method:  check_if_rda()
##  -  check if record has 3XX RDA fields or 040 $e rda
######################################################################
def check_if_rda(rec):
	msg = ''
	rda_rec = False
	rec_040e = ''
	rec_040s = rec.get_fields('040')
	rec_336s = rec.get_fields('336')
	rec_337s = rec.get_fields('337')
	rec_338s = rec.get_fields('338')
	if len(rec_040s)>0:
		if len(rec_040s[0].get_subfields('e')) > 0:
			rec_040e = rec_040s[0].get_subfields('e')[0]
		else:
			rec_040e = '[none]'
		msg += '040 $e field: '+rec_040e+'\n'
	else:
		msg += 'ERROR-MISC: No 040 field exists\n'
	
	if len(rec_336s)>0 or len(rec_337s)>0 or len(rec_338s)>0 or rec_040e=='rda':
		msg += 'RDA fields: YES\n'
		rda_rec = True
	
	return (rda_rec, msg)

######################################################################
##  Method:  check_repl_char()
##  -  check if record has bad encoding replacement character - u"\uFFFD"
##     (i.e., black diamond with question mark in the center)
######################################################################
def check_repl_char(rec):
	msg = ''
	repl_char_exists = False
	rec_fields = rec.get_fields()
	for field in rec_fields:
		if not field.is_control_field():
			if u'\ufffd' in field.value():
				repl_char_exists = True
	if repl_char_exists:
		msg += 'ERROR-MISC: Contains invalid replacement character\n'
		
	return (repl_char_exists, msg)

######################################################################
##  Method:  add_ordered_gmd()
######################################################################
def add_ordered_gmd(sub, pre_gmd_sub_code, post_gmd_sub_code, new_245, gmd_added):
	sub_code = sub[1:2]
	sub_content = sub[2:]
	if not sub=='':
		if sub.startswith(pre_gmd_sub_code) and not gmd_added:
			sub_no_punct = sub_content.rstrip(' ;:/,.=')
			sub_punct = sub_content[len(sub_no_punct):]
			if post_gmd_sub_code == '$b':
				gmd_punct = ' :'
			elif post_gmd_sub_code == '$c':
				gmd_punct = ' /'
			elif post_gmd_sub_code == '':
				gmd_punct = '.'
			else:
				gmd_punct = ''
			new_245.add_subfield(sub_code,sub_no_punct)
			new_245.add_subfield('h','[electronic resource]'+gmd_punct)
			gmd_added = True
		else:
			new_245.add_subfield(sub_code,sub_content)
		return (new_245, gmd_added)
	else:
		return (new_245, gmd_added)
		
######################################################################
##  Method:  convert_2_eres_rec()
######################################################################
def convert_2_eres_rec(rec, rda_rec):
	msg = ''
 	rec_003_value = rec.get_fields('003')[0].value()	# the partner's institutional code from the 003
 	rec_001_value = rec.get_fields('001')[0].value()	# the partner's local record number (BSN) from the 001
	
	if rec_003_value == 'NNU':
		inst_name = 'New York Univeristy Libraries'
		inst_710a = 'New York University.'
		inst_710b = 'Libraries.'
	elif rec_003_value == 'NIC':
		inst_name = 'Cornell University Libraries'
		inst_710a = 'Cornell University.'
		inst_710b = 'Libraries.'
	elif rec_003_value == 'NNC':
		inst_name = 'Columbia University Libraries'
		inst_710a = 'Columbia University.'
		inst_710b = 'Libraries.'
	elif rec_003_value == 'NjP':
		inst_name = 'Princeton University Libraries'
		inst_710a = 'Princeton University.'
		inst_710b = 'Library.'
	elif rec_003_value == 'LeBAU':
		inst_name = "American University of Beirut's Jafet Memorial Library"
		inst_710a = 'Jafet Memorial Library.'
		inst_710b = ''
	else:
		inst_name = ''
		inst_710a = ''
		inst_710b = ''
		msg += 'ERROR-MISC:  003 code - '+rec_003_value+' - did not match any of the partner institutions.\n'
	
	if rec_001_value.startswith('o'):	# this OCLC record did not get processed in step 4
		msg += 'ERROR-MISC:  003/001 field values did not change to institutional code and BSN\n'
		msg += '   Record 003/001: '+rec_003_value+'_'+rec_001_value+'\n'
		for rec_035 in rec.get_fields('035'):
			msg += '   '+str(rec_035)+'\n'
	
	# delete the 005 field
	for rec_005 in rec.get_fields('005'):
		rec.remove_field(rec_005)
	
	# change the cataloging date in bytes 00-05 of the 008 to the current date 
	curr_date = datetime.date.today()
	yy = str(curr_date.year)[2:].zfill(2)
	mm = str(curr_date.month).zfill(2)
	dd = str(curr_date.day).zfill(2)
	rec_008_value = rec.get_fields('008')[0].value()
	new_008_data = yy+mm+dd+rec_008_value[6:]
	new_008 = Field(tag='008', data=new_008_data)
	rec.remove_field(rec.get_fields('008')[0])
	rec.add_ordered_field(new_008)
	
	# change byte 23 in the 008 field to code 'o' for 'online'
	rec_008_value = rec['008'].data
	rec['008'].data = rec_008_value[0:23] + 'o' + rec_008_value[24:]
	
	# add the 006/007 format fields for electronic resource characteristics
	if len(rec.get_fields('006')) > 0:
		for rec_006 in rec.get_fields('006'):
			rec_006_value = rec_006.value()
			msg += 'ERROR-MISC: 006  '+rec_006_value+'\n'
			rec.remove_field(rec_006)
	new_006 = Field(tag='006', data='m        d        ')
	rec.add_ordered_field(new_006)
	
	if len(rec.get_fields('007')) > 0:
		for rec_007 in rec.get_fields('007'):
			rec_007_value = rec_007.value()
			msg += 'ERROR-MISC: 007  '+rec_007_value+'\n'
			rec.remove_field(rec_007)
	new_007 = Field(tag='007', data='cr cn |||m|||a')
	rec.add_ordered_field(new_007)
	
	# delete fields that relate to the print version
	if len(rec.get_fields('016')) > 0:
		for rec_016 in rec.get_fields('016'):
			rec.remove_field(rec_016)
	
	if len(rec.get_fields('019')) > 0:
		for rec_019 in rec.get_fields('019'):
			rec.remove_field(rec_019)
	
	if len(rec.get_fields('025')) > 0:
		for rec_025 in rec.get_fields('025'):
			rec.remove_field(rec_025)
	
	if len(rec.get_fields('029')) > 0:
		for rec_029 in rec.get_fields('029'):
			rec.remove_field(rec_029)
	
	if len(rec.get_fields('042')) > 0:
		for rec_042 in rec.get_fields('042'):
			rec.remove_field(rec_042)
	
	if len(rec.get_fields('049')) > 0:
		for rec_049 in rec.get_fields('049'):
			rec.remove_field(rec_049)
	
	# create new 040 field for NNU
	for rec_040 in rec.get_fields('040'):
		rec.remove_field(rec_040)	# delete the existing 040 field(s)
	if rec_003_value == 'LeBAU':
		cat_lang = 'ara'
	else:
		cat_lang = 'eng'
	if rda_rec:
		new_040 = Field(tag='040', indicators=[' ',' '], subfields=['a','NNU','b',cat_lang,'e','rda','c','NNU'])
	else:
		new_040 = Field(tag='040', indicators=[' ',' '], subfields=['a','NNU','b',cat_lang,'c','NNU'])
	rec.add_ordered_field(new_040)
	
	# correct the 041 language code field when multiple codes exist in the same subfield
	if len(rec.get_fields('041')) > 0:
		for rec_041 in rec.get_fields('041'):
			for rec_041_sub in rec_041:
				mult_langs = False
				new_041_subs = []
				# Note: sub[0] is the subfield code and sub[1] is the subfield content for this subfield
				if len(rec_041_sub[1]) > 3:		# there are multiple language codes in this 041 subfield
					mult_langs = True
					rec_041_sub_langs = re.findall('...',rec_041_sub[1])
					for rec_041_sub_lang in rec_041_sub_langs:
						new_041_subs.append([rec_041_sub[0],rec_041_sub_lang])
				else:
					new_041_subs.append([rec_041_sub[0],rec_041_sub[1]])
			
			if mult_langs:
				rec_041_ind1 = rec_041.indicator1
				rec_041_ind2 = rec_041.indicator2
				new_rec_041 = Field(tag='041', indicators=[rec_041_ind1,rec_041_ind2], subfields=[])
				for new_041_sub in new_041_subs:
					new_rec_041.add_subfield(new_041_sub[0],new_041_sub[1])
				
				rec.remove_field(rec_041)
				rec.add_ordered_field(new_rec_041)
	
 	# correct the 050 indicator 2
 	rec_050s = rec.get_fields('050')
 	for rec_050 in rec_050s:
 		this_index = rec_050s.index(rec_050)
 		# check indicator 2 value and fix if needed
 		if rec_050.indicator2 == ' ':
 			rec.get_fields('050')[this_index].indicator2 = '4'
	
	# correct the 082 indicator 1
	rec_082s = rec.get_fields('082')
	for rec_082 in rec_082s:
		this_index = rec_082s.index(rec_082)
 		# check indicator 1 value and fix if needed
 		if rec_082.indicator1 == ' ':
 			rec.get_fields('082')[this_index].indicator1 = '0'
	
	if not rda_rec:
		# add GMD to 245$h for "[electronic resource]"
		rec_245s = rec.get_fields('245')
		gmd_added = False
		if len(rec_245s) == 0:
			msg += 'ERROR-MISC: Record is missing a 245 field\n'
		elif len(rec_245s) > 1:
			msg += 'ERROR-MISC: Record has multiple 245 fields\n'
		else:
			for rec_245 in rec_245s:
				rec_245_ind1 = rec_245.indicator1
				rec_245_ind2 = rec_245.indicator2
				new_rec_245 = Field(tag='245', indicators=[rec_245_ind1,rec_245_ind2], subfields=[])
				# delete any existing 245 $h GMD subfields
				if len(rec_245.get_subfields('h')) > 0:
					for rec_245h in rec_245.get_subfields('h'):
						msg += 'ERROR-MISC: Original record for the print contains a 245$h GMD: '+rec_245h+'\n'
						rec_245.delete_subfield('h')
				rec_245_str = ''
				for rec_245_sub in rec_245:
					rec_245_str += '|$'+rec_245_sub[0]+rec_245_sub[1]			# sub[0]=the subfield code; sub[1]=the subfield content
					rec_245_list = rec_245_str.split('|')
				
				rec_245_re1 = re.compile('\$a[^\$]*$')							# matches subfield pattern $a not followed by any other subfield
				if rec_245_re1.search(rec_245_str) and not gmd_added:
					for sub in rec_245_list:
						post_gmd_sub_code = ''
						if sub.startswith('$a'):
							sub_index = rec_245_list.index(sub)
							if len(rec_245_list) > sub_index+1:
								post_gmd_sub = rec_245_list[sub_index+1]
								post_gmd_sub_code = post_gmd_sub[0:2]
						new_rec_245, gmd_added = add_ordered_gmd(sub,'$a', post_gmd_sub_code, new_rec_245, gmd_added)
				
				rec_245_re2 = re.compile('\$a[^\$]*\$[^np]')					# matches subfield pattern $a not followed by $n or $p
				if rec_245_re2.search(rec_245_str) and not gmd_added:
					for sub in rec_245_list:
						post_gmd_sub_code = ''
						if sub.startswith('$a'):
							sub_index = rec_245_list.index(sub)
							if len(rec_245_list) > sub_index+1:
								post_gmd_sub = rec_245_list[sub_index+1]
								post_gmd_sub_code = post_gmd_sub[0:2]
						new_rec_245, gmd_added = add_ordered_gmd(sub,'$a', post_gmd_sub_code, new_rec_245, gmd_added)

				rec_245_re3 = re.compile('\$a[^\$]*\$n[^\$]*\$[^np]')			# matches subfield pattern $a $n not followed by $n or $p
				if rec_245_re3.search(rec_245_str) and not gmd_added:
					for sub in rec_245_list:
						post_gmd_sub_code = ''
						if sub.startswith('$n'):
							sub_index = rec_245_list.index(sub)
							if len(rec_245_list) > sub_index+1:
								post_gmd_sub = rec_245_list[sub_index+1]
								post_gmd_sub_code = post_gmd_sub[0:2]
						new_rec_245, gmd_added = add_ordered_gmd(sub,'$n', post_gmd_sub_code, new_rec_245, gmd_added)
				
				rec_245_re4 = re.compile('\$a[^\$]*\$p[^\$]*\$[^np]')			# matches subfield pattern $a $p not followed by $n or $p
				if rec_245_re4.search(rec_245_str) and not gmd_added:
					for sub in rec_245_list:
						post_gmd_sub_code = ''
						if sub.startswith('$p'):
							sub_index = rec_245_list.index(sub)
							if len(rec_245_list) > sub_index+1:
								post_gmd_sub = rec_245_list[sub_index+1]
								post_gmd_sub_code = post_gmd_sub[0:2]
						new_rec_245, gmd_added = add_ordered_gmd(sub,'$p', post_gmd_sub_code, new_rec_245, gmd_added)
				
				rec_245_re5 = re.compile('\$a[^\$]*\$n[^\$]*\$p[^\$]*\$[^np]')	# matches subfield pattern $a $n $p not followed by $n or $p
				if rec_245_re5.search(rec_245_str) and not gmd_added:
					for sub in rec_245_list:
						post_gmd_sub_code = ''
						if sub.startswith('$p'):
							sub_index = rec_245_list.index(sub)
							if len(rec_245_list) > sub_index+1:
								post_gmd_sub = rec_245_list[sub_index+1]
								post_gmd_sub_code = post_gmd_sub[0:2]
						new_rec_245, gmd_added = add_ordered_gmd(sub,'$p', post_gmd_sub_code, new_rec_245, gmd_added)
				
				rec.remove_field(rec_245)
				rec.add_ordered_field(new_rec_245)
		
		if not gmd_added:
			msg += 'ERROR-MISC: GMD did not get added to non-RDA record\n'

		# NEED TO FIGURE OUT HOW TO ADD GMD to corresponding 880 field if it exists
	
	# delete subfield $c from 300 fields, modify punctuation in subfields $a and $b, and add 'online resource' to subfield $a
 	for rec_300 in rec.get_fields('300'):
 		if not rec_300.get_subfields('a')[0].startswith('online'):
	 		rec_300.delete_subfield('c')
	 		rec_300a = rec_300.get_subfields('a')[0]
	 		rec_300a = rec_300a.strip(' ;')
	 		rec_300a_pgs = rec_300a.split(' :')
	 		rec_300.delete_subfield('a')
	 		try:
	 			rec_300b = rec_300.get_subfields('b')[0]
	 			rec_300b = rec_300b.strip(' ;')
	 			rec_300.delete_subfield('b')
	 			rec_300a_mod = 'online resource ('+rec_300a_pgs[0]+') :'
	 			rec_300.add_subfield('a', rec_300a_mod)
	 			rec_300.add_subfield('b', rec_300b)
	 		except:
	 			# there is no subfield $b in the 300
	 			rec_300a_mod = 'online resource ('+rec_300a_pgs[0]+')'
	 			rec_300.add_subfield('a', rec_300a_mod)
	
	if rda_rec:
		# Delete any existing 336, 337, and 338 fields for the print characteristics
		if len(rec.get_fields('336')) > 0:
			for rec_336 in rec.get_fields('336'):
				rec.remove_field(rec_336)
		if len(rec.get_fields('337')) > 0:
			for rec_337 in rec.get_fields('337'):
				rec.remove_field(rec_337)
		if len(rec.get_fields('338')) > 0:
			for rec_338 in rec.get_fields('338'):
				rec.remove_field(rec_338)
		
		# Add 336, 337, and 338 fields for the e-resource characteristics for content, media, and carrier
		new_rec_336 = Field(tag='336', indicators=[' ',' '], subfields=['a','text','2','rdacontent'])
		new_rec_337 = Field(tag='337', indicators=[' ',' '], subfields=['a','computer','2','rdamedia'])
		new_rec_338 = Field(tag='338', indicators=[' ',' '], subfields=['a','online resource','2','rdacarrier'])
		
		rec.add_ordered_field(new_rec_336)
		rec.add_ordered_field(new_rec_337)
		rec.add_ordered_field(new_rec_338)
	
	# add ACO note field
	new_500_aco = Field(tag='500', indicators=[' ',' '], subfields=['a','Part of the Arabic Collections Online (ACO) project, contributed by '+inst_name+'.'])
	rec.add_ordered_field(new_500_aco)
	
	# delete any print record's reference to other formats
	if len(rec.get_fields('530')) > 0:
		for rec_530 in rec.get_fields('530'):
			rec.remove_field(rec_530)
	
	# delete any existing 533 fields (e.g. for microform)
	for rec_533 in rec.get_fields('533'):
		rec.remove_field(rec_533)
	
	# add 533 field related to electronic reproduction
	curr_year = datetime.date.today().year
	new_533 = Field(tag='533', indicators=[' ',' '], subfields=['a', 'Electronic reproduction.', 'b', 'New York, N.Y. :', 'c', 'New York University,', 'd', str(curr_year)+'.', '5', 'NNU'])
	rec.add_ordered_field(new_533)
	
	# delete any existing 539 fields (e.g. for microform)
	for rec_539 in rec.get_fields('539'):
		rec.remove_field(rec_539)
	
# 	new_539 = Field(tag='539', indicators=[' ',' '], subfields=['a', 's', 'b', str(curr_year), 'd', 'nyu', 'e', 'n', 'g', 'o'])
# 	rec.add_ordered_field(new_539)
	
	# add headings referring to the ACO project and partners
	if not inst_710b == '':
		new_710 = Field(tag='710', indicators=['2',' '], subfields=['a', inst_710a, 'b', inst_710b])
	else:
		new_710 = Field(tag='710', indicators=['2',' '], subfields=['a', inst_710a])
	
 	rec.add_ordered_field(new_710)
	
	new_730 = Field(tag='730', indicators=['0',' '], subfields=['a','Arabic Collections Online.'])
	rec.add_ordered_field(new_730)
	
	# add a new 776 field referencing the relationship to the print version
	new_776 = Field(tag='776', indicators=['0','8'], subfields=['i', 'Print version:'])
		
	# capture name entry from 100 or 110 if they exist and insert into new 776 subfield $a to reference print version
	if len(rec.get_fields('100', '110')) > 0:
		new_776a = rec.get_fields('100', '110')[0].value()
		if new_776a.startswith('8'):
			new_776a = new_776a[7:]
		new_776.add_subfield('a', new_776a)
	
	# capture title entry from 245 and insert into new 776 subfield $t to reference print version
	new_776t = rec.get_fields('245')[0].get_subfields('a')[0]
	new_776t = new_776t.rstrip(' /:.,')
	new_776.add_subfield('t', new_776t)
	
	# capture institutional ID entry from 003/001 and insert into new 776 subfield $w to reference print version
	new_776.add_subfield('w', '('+rec_003_value+')'+rec_001_value)
	
	if len(rec.get_fields('010')) > 0:
		if len(rec.get_fields('010')[0].get_subfields('a')) > 0:
			new_776w_010 = rec.get_fields('010')[0].get_subfields('a')[0]
			new_776.add_subfield('w', '(DLC)'+new_776w_010)
			rec.remove_field(rec.get_fields('010')[0])

	if len(rec.get_fields('035')) > 0:
		for rec_035 in rec.get_fields('035'):
			rec_035a = rec_035.get_subfields('a')[0]
			if rec_035a.startswith('(OCoLC)'):
				new_776w_oclc = rec_035a
				new_776.add_subfield('w', new_776w_oclc)
			rec.remove_field(rec_035)
	
	new_020z_fields = []							# variable to collect the 020 fields as "invalid" subfield z's instead of subfield a's
	new_020z_subfields = []							# variable to collect the print ISBNs to add to the 776 field
	if len(rec.get_fields('020')) > 0:					# record contains 020 ISBN fields
		for rec_020 in rec.get_fields('020'):			# iterate through each of the 020 fields
			msg += '020s: YES\n'
			if len(rec_020.get_subfields('a')) > 0:			# the 020 field has a subfield a
				for rec_020a in rec_020.get_subfields('a'):	# iterate through the subfield a's
					msg += '020a: '+str(rec_020a)+'\n'
					new_020z_field = Field(tag='020', indicators=[' ',' '], subfields=['z', rec_020a])
					new_020z_fields.append(new_020z_field)
					new_020z_subfields.append(rec_020a)
			rec.remove_field(rec_020)
	
	for new_020z_field in new_020z_fields:
		rec.add_ordered_field(new_020z_field)
	
	for new_776z in new_020z_subfields:
		new_776.add_subfield('z', new_776z)
	
	rec.add_ordered_field(new_776)
	
	# delete any 090 $h/$i fields
	if len(rec.get_fields('090')) > 0:
		for rec_090 in rec.get_fields('090'):
			if len(rec_090.get_subfields('h')) > 0:
				for rec_090h in rec_090.get_subfields('h'):
					rec_090.delete_subfield('h')
			if len(rec_090.get_subfields('i')) > 0:
				for rec_090i in rec_090.get_subfields('i'):
					rec_090.delete_subfield('i')
			if rec_090.format_field()=='':
				rec.remove_field(rec_090)
	
	# delete any local fields (9XXs, OWN, AVA)
	rec_9XXs = rec.get_fields('852','903','907','910','938','945','950','955','981','987','994','998','OWN','AVA')
	if len(rec_9XXs) > 0:
		for rec_9XX in rec_9XXs:
			rec.remove_field(rec_9XX)
			
	return (rec, msg)

######################################################################
##  Method:  sort_6_subs()
##  -  sort all subfield $6's to beginning of field
######################################################################
def sort_6_subs(rec):
	msg = ''
	new_rec = Record(to_unicode=True, force_utf8=True)
	new_rec_fields = []
	rec_fields = rec.get_fields()
	for field in rec_fields:
		script_field = False
		if not field.is_control_field() and (len(field.get_subfields('6')) > 0):	# the field contains a subfield $6
			script_field = True
			ind1 = field.indicator1
			ind2 = field.indicator2
			tag = field.tag
			first_sub = True		# variable to keep track of whether you're on the first subfield in the field
			needs_sorted = True		# variable to keep track of whether the field needs sorted or if the $6 is already correctly the first subfield
			field_subs = []			# list variable to capture all the subfields in the field *except* for the subfield $6
			for subfield in field:
				# check if $6 is the first subfield - if so, the field is OK and does *not* need to be sorted
				if needs_sorted and first_sub and subfield[0] == '6':
					needs_sorted = False
				
				elif needs_sorted:
					if first_sub:
						# this is the first subfield and is *not* $6, so the field needs sorted - creates one instance of a new_field object only when the 1st subfield is encountered
						new_field = Field(tag=tag, indicators=[ind1,ind2], subfields=[])
					
					# when subfield $6 is finally encountered in the field (not the 1st), add it to the new_field object now so it becomes the first subfield
					# Note: subfield[0] is the subfield code and subfield[1] is the subfield content for this subfield
					if subfield[0]=='6':
						new_field.add_subfield(subfield[0],subfield[1])
					
					# if the subfield is *not* $6, add it to the list of subfields to be added later to the new_field
					else:
						field_subs.append([subfield[0],subfield[1]])
				
				first_sub = False
			
			if needs_sorted:
				# then the $6 was *not* the 1st subfield and we need to now add the remaining subfields to the new_field object
				for sub in field_subs:
					# add the remaining subfields to the new_field object
					new_field.add_subfield(sub[0],sub[1])
				new_rec_fields.append(new_field)	# add the new field to the record
		
		if not script_field or not needs_sorted:
			new_rec_fields.append(field)
	
	for new_f in new_rec_fields:
		new_rec.add_field(new_f)
	
	return new_rec

######################################################################
##  Method:  second_sort_6_check()
##  -  check for any subfield $6's that did not sort to beginning of field
######################################################################
def second_sort_6_check(rec):
	msg = ''
	rec_fields = rec.get_fields()
	for field in rec_fields:
		if not field.is_control_field() and len(field.get_subfields('6')) > 0:
			first_sub = True
			for subfield in field:
				if first_sub and not subfield[0] == '6':
					msg += 'ERROR-MISC: Unsorted $6 subfield: '+field.value()+'\n'
				first_sub = False
	
	return(rec, msg)

######################################################################
##  Method:  insert_url()
######################################################################
def insert_url(rec, handles):
	msg = ''
	rec_003 = rec.get_fields('003')[0].value()
	rec_001 = rec.get_fields('001')[0].value()
	handle_match = False
	
	for line in handles:
		handle_data = line.split(',')
		handle_003 = handle_data[0]
		handle_001 = handle_data[1]
		handle = handle_data[2]
		if rec_003 == handle_003 and rec_001 == handle_001:
			handle_match = True
			# add URL handle to the MARC record in an 856 $u field
			new_856 = Field(tag='856', indicators=['4','0'], subfields=['u',handle])
			rec.add_ordered_field(new_856)
			
			# add 959 field for WEB/GENI holdings record data for batch-loading
			# 959a = Library
			# 959b = Sublibrary
			# 959c = Collection
			# 959t = Type of Call Number (852-1st indicator)
			# 959h = Call Number Classification
			# 959i = Call Number Cutter
			# 959m = Call Number Suffix (i.e., "Electronic access" for WEB holdings)
			# 959s = Item Status
			# new959 = Field(tag='959', indicators=[' ',' '], subfields=['a','NNU','b','WEB','c','GENI','t','0','h',callNoClass,'i',callNoCutter,'x','Electronic access','s','01'])
			new_959 = Field(tag='959', indicators=[' ',' '], subfields=['a','NNU','b','WEB','c','GENI','t','0','m','Electronic access','s','01'])
			rec.add_ordered_field(new_959)
	
	if not handle_match:
		msg += 'ERROR-MISC:  No handles in CSV file matched the record 003/001\n'
	return (rec, msg)

######################################################################
##  Method:  insert_src_entities()
######################################################################
def insert_src_entities(rec, bsn_se_lines):
	msg = ''
	rec_003 = rec.get_fields('003')[0].value()
	rec_001 = rec.get_fields('001')[0].value()
	se_match = False
	
	inst_regex = re.compile('^[^_]*')	# regular expression for matching leading characters up to the first underscore
	for line in bsn_se_lines:
		bsn_se_data = line.split(',')
		se_001 = bsn_se_data[0]
		se_IDs = bsn_se_data[1]
		se_inst = re.findall(inst_regex,se_IDs)[0]
		if se_inst == 'nyu':
			se_003 = 'NNU'
			# add leading zeros to create a 9-digit BSN for NYU records
			se_001 = "{0:0>9}".format(se_001)
		if se_inst == 'columbia':
			se_003 = 'NNC'
		if se_inst == 'cornell':
			se_003 = 'NIC'
		if se_inst == 'princeton':
			se_003 = 'NjP'
		if se_inst == 'aub':
			se_003 = 'LeBAU'
		if rec_003 == se_003 and rec_001 == se_001:
			se_match = True
			msg += 'Source entities (book IDs): '
			se_IDs_list = se_IDs.split('|')
			for se_ID in se_IDs_list:
				se_ID = se_ID.strip()
				rec.get_fields('999')[0].add_subfield('s', se_ID)
				msg += se_ID + ', '
			msg = msg.rstrip(', ')
			msg += '\n'
				

	if not se_match:
		msg += 'ERROR-MISC:  No BSNs in bsn-se-map.csv file matched the record 003/001\n'
	
	return (rec, msg)
			

######################################################################
##  Method process_rec()
######################################################################
def process_rec(rec, type):
	rec_orig = deepcopy(rec)
	dup_num = False
	no_880_rec = False
	missing_key_880_rec = False
	unlinked_880_rec = False
	indiv_rec_analysis_msg = ''			# string variable to collect individual analysis messages for each record
	
	rec_003_value = rec.get_fields('003')[0].value()	# either 'OCLC' or the partner's institution code from the 003 field
	rec_001_value = rec.get_fields('001')[0].value()	# either the OCLC number or the inst_id from the 001 field
	if type=='oclc':
		################################################
		# Check for duplicate OCLC record in batch
		for num in aco_globals.oclc_nums_processed:
			if rec_001_value == num:
				dup_num = True
		if not dup_num:
			aco_globals.oclc_nums_processed.add(rec_001_value)
		
	if type=='orig' or not dup_num:
		################################################
		# Add institutional ID and OCLC number to 999 field
		rec_orig, rec, oclc_id, inst_id, oclc_match, msg_1 = process_001_003_fields(rec_orig, rec, aco_globals.oclc_nums_bsns_all)
		indiv_rec_analysis_msg += msg_1
		if not oclc_match:
			aco_globals.recs_no_oclc_match_count += 1
		
		################################################
		# Check if record is missing any 880 script fields
		script_rec, missing_key_880s, msg_2 = check_for_missing_880s(rec)
		indiv_rec_analysis_msg += msg_2
		if not script_rec:
			no_880_rec = True
		else:
			aco_globals.recs_880s_count += 1
		
		if missing_key_880s:
			missing_key_880_rec = True
		
		################################################
		# Check if record has any unlinked 880 fields (having "00" in the 880 $6 numbering)
		unlinked_exist, msg_3 = check_for_unlinked_880s(rec)
		indiv_rec_analysis_msg += msg_3
		if unlinked_exist:
			unlinked_880_rec = True
		
		################################################
		# Check if record has any untraced 490 fields without corresponding 8XX fields
		msg_4 = check_series_hdgs(rec)
		indiv_rec_analysis_msg += msg_4
		
		################################################
		# Check if record contains RDA fields
		rda_rec, msg_5 = check_if_rda(rec)
		indiv_rec_analysis_msg += msg_5
		if rda_rec:
			aco_globals.recs_rda_count += 1	
		
		################################################
		# Check if record contains bad encoding script character (black diamond around question-mark)
		# Evidenced by presence of Python source code u"\uFFFD" (See: http://www.fileformat.info/info/unicode/char/0fffd/index.htm)
		repl_char, msg_6 = check_repl_char(rec)
		indiv_rec_analysis_msg += msg_6
		if repl_char:
			aco_globals.recs_repl_char_count += 1
		
		################################################
		# Add/Delete/Modify MARC fields in print record to convert to an e-resource record
		rec, msg_7 = convert_2_eres_rec(rec, rda_rec)
		indiv_rec_analysis_msg += msg_7
		
		################################################
		# Sort any $6 subfields that do not appear first in the field
		rec = sort_6_subs(rec)
		
		rec, msg_8 = second_sort_6_check(rec)
		indiv_rec_analysis_msg += msg_8
				
		################################################
		# Match the 001/003 fields and insert the corresponding URL handle in an 856 field
		rec, msg_9 = insert_url(rec, aco_globals.handles_lines)
		indiv_rec_analysis_msg += msg_9
		
		################################################
		# Match the BSNs and insert the corresponding SE (source entity) book IDs into the 999 field
		rec, msg_10 = insert_src_entities(rec, aco_globals.bsn_se_lines)
		indiv_rec_analysis_msg += msg_10
		
		################################################
		# Change LDR values
		ldr = list(rec.leader)
		ldr[5] = 'n'
		ldr[6] = 'a'
		ldr[7] = 'm'
		#ldr[9] = 'a'
		rec.leader = ''.join(ldr)
		
		################################################
		# Remove any existing 999 $e subfields and Add new 999 $e subfield with error type codes
		# --  NOTE: adding the field to the rec_orig (deep copy of rec) seems to also add to rec...??
		add_999e = False
		
		rec_orig_999s = rec_orig.get_fields('999')
		if len(rec_orig_999s) == 0:
			indiv_rec_analysis_msg += 'ERROR-MISC: The 999 field did not get added to the original record during processing\n'
		elif len(rec_orig_999s) > 1:
			indiv_rec_analysis_msg += 'ERROR-MISC: Original record contains multiple 999 fields\n'
		elif len(rec_orig_999s) == 1:
			if len(rec_orig.get_fields('999')[0].get_subfields('e')) > 0:
				for rec_orig_999e in rec_orig.get_fields('999')[0].get_subfields('e'):
					rec_orig.get_fields('999')[0].delete_subfield('e')
			add_999e = True
		
# 		rec_999s = rec.get_fields('999')
# 		if len(rec_999s) == 0:
# 			indiv_rec_analysis_msg += 'ERROR-MISC: The 999 field did not get added to the converted record during processing\n'
# 		elif len(rec_999s) > 1:
# 			indiv_rec_analysis_msg += 'ERROR-MISC: Converted record contains multiple 999 fields\n'
# 		elif len(rec_999s) == 1:
# 			if len(rec.get_fields('999')[0].get_subfields('e')) > 0:
# 				for rec_999e in rec.get_fields('999')[0].get_subfields('e'):
# 					rec.get_fields('999')[0].delete_subfield('e')
# 			add_999e = True
		
		if add_999e:
			error_types = ''
			if 'ERROR-880' in indiv_rec_analysis_msg:
				error_types += '(ERROR-880)'
			if 'ERROR-SERIES' in indiv_rec_analysis_msg:
				error_types += '(ERROR-SERIES)'
			if 'ERROR-MISC' in indiv_rec_analysis_msg:
				error_types += '(ERROR-MISC)'
			if not error_types == '':
				rec_orig.get_fields('999')[0].add_subfield('e', error_types)
		
		indiv_rec_analysis_msg += '---------------------------------------------------------------------\n'
		
		################################################
		# Write out ERROR message and MARC records depending on status
		if no_880_rec:
			aco_globals.recs_no_880s_count += 1
			aco_globals.marcRecsOut_no_880s.write(rec_orig)
			aco_globals.recs_no_880s_txt.write(indiv_rec_analysis_msg)
		if missing_key_880_rec:
			aco_globals.recs_missing_key_880s_count += 1
			aco_globals.marcRecsOut_missing_key_880s.write(rec_orig)
			aco_globals.recs_missing_key_880s_txt.write(indiv_rec_analysis_msg)
		if unlinked_880_rec:
			aco_globals.recs_unlinked_880s_count += 1
			aco_globals.marcRecsOut_unlinked_880s.write(rec_orig)
			aco_globals.recs_unlinked_880s_txt.write(indiv_rec_analysis_msg)
		if 'ERROR-SERIES' in indiv_rec_analysis_msg:
			aco_globals.recs_series_errors_count += 1
			aco_globals.marcRecsOut_series_errors.write(rec_orig)
			aco_globals.recs_series_errors_txt.write(indiv_rec_analysis_msg)
		if 'ERROR-MISC' in indiv_rec_analysis_msg:
			aco_globals.recs_misc_errors_count += 1
			aco_globals.marcRecsOut_misc_errors.write(rec_orig)
			aco_globals.recs_misc_errors_txt.write(indiv_rec_analysis_msg)
		
		if 'ERROR' in indiv_rec_analysis_msg:
			aco_globals.recs_errors_all_count += 1
			aco_globals.marcRecsOut_errors_all.write(rec_orig)
			aco_globals.recs_errors_all_txt.write(indiv_rec_analysis_msg)
		else:
			aco_globals.marcRecsOut_final_subset.write(rec)
			aco_globals.recs_final_this_subset_count += 1
		
		aco_globals.marcRecsOut_final_all.write(rec)
				
		################################################
		# Write out individual .mrc record
		try: os.makedirs(aco_globals.batch_folder+'/mrc_out')
		except OSError as exception:
			if exception.errno != errno.EEXIST:
				raise
		indiv_marcRecOut = pymarc.MARCWriter(file(aco_globals.batch_folder+'/mrc_out/'+inst_id+'_mrc.mrc', 'w'))
		indiv_marcRecOut.write(rec)
		indiv_marcRecOut.close()
		
		################################################
		# Convert MARC to MARCXML and write out individual MARCXML record
		rec_xml = pymarc.record_to_xml(rec, namespace=True)
		pretty_rec_xml = xml.dom.minidom.parseString(rec_xml)
		pretty_rec_xml = pretty_rec_xml.toprettyxml(encoding='utf-8')
		try: os.makedirs(aco_globals.batch_folder+'/marcxml_out')
		except OSError as exception:
			if exception.errno != errno.EEXIST:
				raise
		indiv_marcRecOut_xml = codecs.open(aco_globals.batch_folder+'/marcxml_out/'+inst_id+'_marcxml.xml', 'w')
		indiv_marcRecOut_xml.write(pretty_rec_xml)
		indiv_marcRecOut_xml.close()
				
		aco_globals.indiv_rec_analysis_msgs += indiv_rec_analysis_msg
	
	return dup_num
		
######################################################################
##  Method:  calculate_percentage()
######################################################################
def calculate_percentage(x,y):
	percentage = 100 * float(x)/float(y)
	percentage = round(percentage,1)
	return str(percentage)
