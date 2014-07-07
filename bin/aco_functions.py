import pymarc
from pymarc import Record, Field
import re
import datetime
import string

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
######################################################################
def process_001_003_fields(rec, oclc_nums_bsns):
	msg = ''
	oclc_id = ''
	inst_id = ''
	oclc_match = False
	rec_003_value = rec.get_fields('003')[0].value()	# the institutional code from the 003 (either "OCLC" or a partner institution)
	rec_001_value = rec.get_fields('001')[0].value()	# the local record number from the 001 (either the OCLC number or the partner's BSN)
	
	# Process OCLC records exported from Connexion
	if rec_001_value.startswith('o'):
		oclc_id = rec_003_value+'_'+rec_001_value
		msg += 'OCLC ID: '+rec_003_value+'_'+rec_001_value +'\n'
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
						msg += '   oclc_rec_035_num: '+str(this_az)+'\n'
		
		for line in oclc_nums_bsns:		# iterate through each of the lines in the txt file containing 001s/003s and OCLC numbers from original records
			if line.startswith('003'):		# this is the first header line in the txt file
				# skip the header row
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
							inst_id = line_003+'_'+line_001
							msg += 'Institution ID: '+line_003+'_'+line_001+'\n'
							# add an 035 field to the OCLC record containing the 001/003 information from the original record
							line_bsn = '('+line_003+')'+line_001
							new_035_bsn = Field(tag='035', indicators=[' ',' '], subfields=['a',line_bsn])
							rec.add_ordered_field(new_035_bsn)
							
							# delete the existing 001/003 fields from the OCLC record containing the OCLC number and symbol
							rec.remove_field(rec.get_fields('003')[0])
							rec.remove_field(rec.get_fields('001')[0])
							
							# add new 001/003 fields to the OCLC record containing the partner's bsn and institution code
							new_003 = Field(tag='003', data=line_003)
							rec.add_ordered_field(new_003)
							new_001 = Field(tag='001', data=line_001)
							rec.add_ordered_field(new_001)
		if not oclc_match:
			msg += 'ERROR:  OCLC numbers did not match any original record\n'
	
	# Process Original Records (no OCLC record found in Connexion)
	else:
		inst_id = rec_003_value+'_'+rec_001_value
		msg += 'Institution ID: '+rec_003_value+'_'+rec_001_value+'\n'
		# for orig records, delete all existing 035 fields
		if len(rec.get_fields('035')) > 0:
			for rec_035 in rec.get_fields('035'):
				msg += '   orig_rec_035 num: '+str(rec_035)+'\n'
				rec.remove_field(rec_035)	# delete this 035 field
	
		# for orig records, copy the 001/003 BSN field data to an 035 field
		new_035_bsn = Field(tag='035', indicators=[' ',' '], subfields=['a','('+rec_003_value+')'+rec_001_value])
		rec.add_ordered_field(new_035_bsn)
	
	return (rec, oclc_id, inst_id, oclc_match, msg)

######################################################################
##  Method:  check_880s()
##  -  check if record has 880 script fields
######################################################################
def check_880s(rec):
	msg = ''
	script_rec = True
	rec_880s = rec.get_fields('880')
	if len(rec_880s) == 0:			# the record does *not* contain 880 script fields
		script_rec = False
		msg = '880 script fields: NO\n'
	else:
		msg = '880 script fields: YES\n'
	
	return (script_rec, msg)

######################################################################
##  Method:  check_rda()
##  -  check if record has RDA fields
######################################################################
def check_rda(rec):
	msg = ''
	rda_rec = False
	rec_040e = ''
	rec_040s = rec.get_fields('040')
	rec_336s = rec.get_fields('336')
	rec_337s = rec.get_fields('337')
	rec_338s = rec.get_fields('338')
	if len(rec_040s)>0:
		if len(rec_040s[0].get_subfields('e')) > 0:
			rec_040e = rec_040s[0].get_subfields('e')[0].value()
		else:
			rec_040e = '[none]'
	else:
		msg += 'ERROR: No 040 field exists\n'
	
	if len(rec_336s)>0 or len(rec_337s)>0 or len(rec_338s)>0 or rec_040e=='rda':
		msg += 'RDA fields: YES\n   040e field: '+rec_040e+'\n'
		rda_rec = True
	
	return (rda_rec, msg)

######################################################################
##  Method:  check_repl_char()
##  -  check if record has bad encoding replacement character - u"\uFFFD"
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
		msg += 'ERROR: Contains invalid replacement character\n'
		
	return (repl_char_exists, msg)

######################################################################
##  Method:  add_ordered_gmd()
######################################################################
def add_ordered_gmd(sub, pre_sub_code, new_245, gmd_added):
	sub_code = sub[1:2]
	sub_content = sub[2:]
	if not sub=='':
		if sub.startswith(pre_sub_code) and not gmd_added:
			sub_no_punct = sub_content.rstrip(' ;:/,.=')
			sub_punct = sub_content[len(sub_no_punct):]							
			new_245.add_subfield(sub_code,sub_no_punct)
			new_245.add_subfield('h','[electronic resource]'+sub_punct)
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
	
	if rec_003_value == 'COO':
		inst_name = 'Cornell University Libraries'
		inst_710a = 'Cornell University.'
		inst_710b = 'Libraries.'
	elif rec_003_value == 'NNC':
		inst_name = 'Columbia University Libraries'
		inst_710a = 'Columbia University.'
		inst_710b = 'Libraries.'
	elif rec_003_value == 'NNU':
		inst_name = 'New York Univeristy Libraries'
		inst_710a = 'New York University.'
		inst_710b = 'Libraries.'
	elif rec_003_value == 'PUL':
		inst_name = 'Princeton University Libraries'
		inst_710a = 'Princeton University.'
		inst_710b = 'Library.'
	else:
		inst_name = ''
		inst_710a = ''
		inst_710b = ''
		msg += 'ERROR:  003 code - '+rec_003_value+' - did not match any of the partner institutions.\n'
	
	if rec_001_value.startswith('o'):	# this OCLC record did not get processed in step 4
		msg += 'ERROR:  003/001 field values did not change to institutional code and BSN\n'
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
	
	# add the 006/007 format fields for electronic resource characteristics
	new_006 = Field(tag='006', data='m        d        ')
	rec.add_ordered_field(new_006)
	if len(rec.get_fields('007')) > 0:
		for rec_007 in rec.get_fields('007'):
			rec_007_value = rec_007.value()
			msg += 'ERROR: 007  '+rec_007_value+'\n'
			rec.remove_field(rec_007)
	new_007 = Field(tag='007', data='cr cn |||m|||a')
	rec.add_ordered_field(new_007)
	
	# change byte 23 in the 008 field to code 'o' for 'online'
	rec_008_value = rec['008'].data
	rec['008'].data = rec_008_value[0:23] + 'o' + rec_008_value[24:]
	
	# delete fields that relate to the print version
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
	if rda_rec:
		new_040 = Field(tag='040', indicators=[' ',' '], subfields=['a','NNU','b','eng','e','rda','c','NNU'])
	else:
		new_040 = Field(tag='040', indicators=[' ',' '], subfields=['a','NNU','b','eng','c','NNU'])
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
	
	# correct the 050 indicators
	if len(rec.get_fields('050')) > 0:
		#rec.get_fields('050')[0].indicators[0] = ' '
		#rec.get_fields('050')[0].indicators[1] = '4'
		# THIS DOES NOT CHANGE THE INDICATORS - NOT SURE HOW TO DO SO
		rec.get_fields('050')[0].indicator1 = ' '
		rec.get_fields('050')[0].indicator2 = '4'
	
	if not rda_rec:
		# add GMD to 245$h for "[electronic resource]"
		rec_245s = rec.get_fields('245')
		gmd_added = False
		if len(rec_245s) == 0:
			msg += 'ERROR: Record is missing a 245 field\n'
		elif len(rec_245s) > 1:
			msg += 'ERROR: Record has multiple 245 fields\n'
		else:
			for rec_245 in rec_245s:
				rec_245_ind1 = rec_245.indicator1
				rec_245_ind2 = rec_245.indicator2
				new_rec_245 = Field(tag='245', indicators=[rec_245_ind1,rec_245_ind2], subfields=[])
				# delete any existing 245 $h GMD subfields
				if len(rec_245.get_subfields('h')) > 0:
					rec_245.delete_subfield('h')
				rec_245_str = ''
				for rec_245_sub in rec_245:
					rec_245_str += '|$'+rec_245_sub[0]+rec_245_sub[1]
					rec_245_list = rec_245_str.split('|')
				
				rec_245_re1 = re.compile('\$a[^\$]*$')							# matches subfield pattern $a not followed by any other subfield
				if rec_245_re1.search(rec_245_str) and not gmd_added:
					for sub in rec_245_list:
						new_rec_245, gmd_added = add_ordered_gmd(sub,'$a',new_rec_245, gmd_added)
				
				rec_245_re2 = re.compile('\$a[^\$]*\$[^np]')					# matches subfield pattern $a not followed by $n or $p
				if rec_245_re2.search(rec_245_str) and not gmd_added:
					for sub in rec_245_list:
						new_rec_245, gmd_added = add_ordered_gmd(sub,'$a',new_rec_245, gmd_added)

				rec_245_re3 = re.compile('\$a[^\$]*\$n[^\$]*\$[^np]')			# matches subfield pattern $a $n not followed by $n or $p
				if rec_245_re3.search(rec_245_str) and not gmd_added:
					for sub in rec_245_list:
						new_rec_245, gmd_added = add_ordered_gmd(sub,'$n',new_rec_245, gmd_added)
				
				rec_245_re4 = re.compile('\$a[^\$]*\$p[^\$]*\$[^np]')			# matches subfield pattern $a $p not followed by $n or $p
				if rec_245_re4.search(rec_245_str) and not gmd_added:
					for sub in rec_245_list:
						new_rec_245, gmd_added = add_ordered_gmd(sub,'$p',new_rec_245, gmd_added)
				
				rec_245_re5 = re.compile('\$a[^\$]*\$n[^\$]*\$p[^\$]*\$[^np]')	# matches subfield pattern $a $n $p not followed by $n or $p
				if rec_245_re5.search(rec_245_str) and not gmd_added:
					for sub in rec_245_list:
						new_rec_245, gmd_added = add_ordered_gmd(sub,'$p',new_rec_245, gmd_added)
				
				rec.remove_field(rec_245)
				rec.add_ordered_field(new_rec_245)
		
		if not gmd_added:
			msg += 'ERROR: GMD not added to non-RDA record\n'

		# NEED TO FIGURE OUT HOW TO ADD GMD to corresponding 880 field if it exists
	
	# delete subfield $c from 300 fields, modify punctuation in subfields $a and $b, and add 'online resource' to subfield $a
 	for rec_300 in rec.get_fields('300'):
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
		# NEED TO SEE WHETHER TO ADD 3XX FIELDS FOR THE E-RESOURCE CHARACTERISTICS
		what2do = 'ask everett'
	
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
	
	# add fields related to electronic reproduction
	curr_year = datetime.date.today().year
	new_533 = Field(tag='533', indicators=[' ',' '], subfields=['a', 'Electronic reproduction.', 'b', 'New York, N.Y. :', 'c', 'New York University,', 'd', str(curr_year)+'.', '5', 'NNU'])
	rec.add_ordered_field(new_533)
	
# 	new_539 = Field(tag='539', indicators=[' ',' '], subfields=['a', 's', 'b', str(curr_year), 'd', 'nyu', 'e', 'n', 'g', 'o'])
# 	rec.add_ordered_field(new_539)
	
	# add headings referring to the ACO project and partners
 	new_710 = Field(tag='710', indicators=['2',' '], subfields=['a', inst_710a, 'b', inst_710b])
 	rec.add_ordered_field(new_710)
	
	new_730 = Field(tag='730', indicators=['0',' '], subfields=['a','Arabic Collections Online.'])
	rec.add_ordered_field(new_730)
	
	# add field referencing the relationship to the print version
	new_776 = Field(tag='776', indicators=['0','8'], subfields=['i', 'Print version:'])
	
	# capture subfield data to insert into the new 776 field for the print version
	if len(rec.get_fields('100', '110')) > 0:
		new_776a = rec.get_fields('100', '110')[0].value()
		if new_776a.startswith('8'):
			new_776a = new_776a[7:]
		new_776.add_subfield('a', new_776a)
		
	new_776t = rec.get_fields('245')[0].get_subfields('a')[0]
	new_776t = new_776t.rstrip(' /:.,')
	new_776.add_subfield('t', new_776t)
	
	new_776.add_subfield('w', '('+rec_003_value+')'+rec_001_value)
	
	if len(rec.get_fields('010')) > 0:
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
	rec_9XXs = rec.get_fields('903','910','938','950','955','981','987','994','998','OWN','AVA')
	if len(rec_9XXs) > 0:
		for rec_9XX in rec_9XXs:
			rec.remove_field(rec_9XX)
			
	return (rec, msg)

######################################################################
##  Method:  sort_6_subs()
##  -  sort all subfield $6's to beginning of field
######################################################################
def sort_6_subs(rec):
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

def second_sort_6_check(rec):
	rec_fields = rec.get_fields()
	for field in rec_fields:
		if not field.is_control_field() and len(field.get_subfields('6')) > 0:
			first_sub = True
			for subfield in field:
				if first_sub and not subfield[0] == '6':
					print 'Unchanged field: '+field.value()
				first_sub = False


######################################################################
##  Method:  link_880s()
######################################################################
def link_880s(rec):
	msg = ''
	rec_003_value = rec.get_fields('003')[0].value()
	rec_001_value = rec.get_fields('001')[0].value()
	rec_880s = rec.get_fields('880')
	
	# get lists of 880s that are unlinked and separate those that have a parallel field and need sequenced from those that don't
	unlinked_880s_exist = False
	rec_880s_to_seq = []
	rec_880s_dont_seq = []
	for rec_880 in rec_880s:
		rec_880_6s = rec_880.get_subfields('6')
		for rec_880_6 in rec_880_6s:
			if rec_880_6[4:6]=='00':
				unlinked_880s_exist = True
				rec_880_pf = rec_880_6[0:3]				# get the corresponding parallel MARC field tag
				rec_pfs = rec.get_fields(rec_880_pf)
				if len(rec_pfs) == 0:					# a parallel field does NOT exist, so don't sequence this 880
					rec_880s_dont_seq.append(rec_880_6)
				else:									# a parallel field DOES exist, so this 880 needs sequenced
					rec_880s_to_seq.append(rec_880_6)
	
	# re-sequence 880s incorporating those unlinked 880s that DO have a parallel field
	if unlinked_880s_exist and len(rec_880s_to_seq) > 0:
		msg += 'Unlinked 880s: YES\n'
		seq_i = 1					# variable to keep track of the new 880 sequence number
		for rec_880 in rec_880s:
			unlnkd_880 = False
			seq_880 = True
			seq_i_str = str(seq_i).zfill(2)
			rec_880_6 = rec_880.get_subfields('6')[0]
			if rec_880_6[4:6] == '00':
				msg += '   '+rec_880_6+'\n'
				for rec_880_dont_seq in rec_880s_dont_seq:
					if rec_880_6 == rec_880_dont_seq:
						seq_880 = False
			if seq_880:
				rec_880_ind1 = rec_880.indicator1
				rec_880_ind2 = rec_880.indicator2
				new_rec_880 = Field(tag='880', indicators=[rec_880_ind1,rec_880_ind2], subfields=[])
				new_rec_880_6 = rec_880_6[0:3]+'-'+seq_i_str+'/r'
				new_rec_880.add_subfield('6',new_rec_880_6)
				rec_880.delete_subfield('6')
				for rec_880_sub in rec_880:
					new_rec_880.add_subfield(rec_880_sub[0],rec_880_sub[1])
				rec.remove_field(rec_880)
				rec.add_ordered_field(new_rec_880)
				seq_i += 1
		
		# re-sequence the parallel fields to match the new 880 sequence numbers
		rec_880s = rec.get_fields('880')
		for rec_880 in rec_880s:
			rec_880_6s = rec_880.get_subfields('6')
			for rec_880_6 in rec_880_6s:
				if not rec_880_6[4:6] == '00':
					rec_880_seq_num = rec_880_6[4:6]
					rec_880_pf = rec_880_6[0:3]
					rec_pfs = rec.get_fields(rec_880_pf)
					if len(rec_pfs) == 0:
						msg += 'ERROR: A parallel field does NOT exist for this 880: '+rec_880_6+'\n'
					else:
						# add new subfield $6 with new sequence numbering to parallel field
						rec_pf = rec_pfs[0]
						rec_pf_6s = rec_pf.get_subfields('6')
						for rec_pf_6 in rec_pf_6s:
							rec_pf.delete_subfield('6')
						
						rec_pf_ind1 = rec_pf.indicator1
						rec_pf_ind2 = rec_pf.indicator2
						new_rec_pf = Field(tag=rec_880_pf, indicators=[rec_pf_ind1,rec_pf_ind2], subfields=[])
						new_rec_pf_6 = '880-'+rec_880_seq_num
						new_rec_pf.add_subfield('6',new_rec_pf_6)
						rec_pf.delete_subfield('6')
						for rec_pf_sub in rec_pf:
							new_rec_pf.add_subfield(rec_pf_sub[0],rec_pf_sub[1])
						rec.remove_field(rec_pf)
						rec.add_ordered_field(new_rec_pf)
					
					if len(rec_pfs) > 1:
						msg += 'ERROR: There are multiple parallel fields for this 880: '+rec_880_6+'\n'
	
	return (rec, unlinked_880s_exist, msg)

######################################################################
##  Method:  insert_url()
######################################################################
def insert_url(rec, handles):
	msg = ''
	rec_003 = rec.get_fields('003')[0].value()
	rec_001 = rec.get_fields('001')[0].value()
	handle_match = False
	
	for line in handles:
		handle_data = line.split(",")
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
		msg += 'ERROR:  No handles in CSV file matched the record 003/001\n'
	return (rec, msg)

######################################################################
##  Method:  calculate_percentage()
######################################################################
def calculate_percentage(x,y):
	percentage = 100 * float(x)/float(y)
	percentage = round(percentage,1)
	return str(percentage)
