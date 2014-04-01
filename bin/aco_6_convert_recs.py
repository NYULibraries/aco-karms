#!/usr/bin/python

# Filename: aco_6_convert_recs.py
# This Python script is used to:
#  1) convert the ACO records to "E-Res" versions
#  2) insert the ACO URL handles extracted from a csv file
#     into 856 fields in the corresponding MARC records based on matching 001/003 fields
#  3) compile final set of records for publishing to ACO site

import pymarc
from pymarc.field import Field
import codecs
import datetime

institution = raw_input("Enter the institution code (e.g., NNC for columbia, COO for cornell, NNU for nyu, or princeton): ")
batch_date = raw_input("Enter the date of the batch being processed in the format YYYYMMDD (e.g., 20140317):")
folder_name = institution + "_" + batch_date

rec_analysis_msgs = ''

# INPUT FILES
try:	marcRecsIn_script = pymarc.MARCReader(file(folder_name+'/'+folder_name+'_4_recs_script.mrc'), to_unicode=True, force_utf8=True)
except:	marcRecsIn_script = ''
try:	marcRecsIn_script_added = pymarc.MARCReader(file(folder_name+'/'+folder_name+'_5_recs_script_added.mrc'), to_unicode=True, force_utf8=True)
except:	marcRecsIn_script_added = ''
try:
	marcRecsIn_orig_recs = pymarc.MARCReader(file(folder_name+'/'+folder_name+'_1_orig_recs.mrc'), to_unicode=True, force_utf8=True)
	orig_recs_all = []
	for orig_rec in marcRecsIn_orig_recs:
		orig_recs_all.append(orig_rec)
except:	orig_recs_all = []
try:
	handles_csv = codecs.open(folder_name+'/'+folder_name+'_4_handles.csv', 'r')    # opens the text file containing the URL handles, 001, and 003 fields (read-only)
	handles_lines = handles_csv.readlines()
except:
	handles_csv = ''
	rec_analysis_msgs += 'No handles CSV file exists\n\n'

# OUTPUT FILES
marcRecsOut_final = pymarc.MARCWriter(file(folder_name+'/'+folder_name+'_6_final_recs_for_pub.mrc', 'w'))
marcRecsOut_orig_recs_subset = pymarc.MARCWriter(file(folder_name+'/'+folder_name+'_6_orig_recs_for_comparison.mrc', 'w'))
rec_analysis_txt = codecs.open(folder_name+'/'+folder_name+'_6_rec_analysis.txt', 'w')

orig_subset_count = 0

######################################################################
##  Method:  convert_eres_rec()
######################################################################
def convert_eres_rec(rec):
	global rec_analysis_msgs
	errors_found = False
	
 	rec_003_value = rec.get_fields('003')[0].value()	# the institutional code from the 003 (either "OCLC" or a partner institution)
 	rec_001_value = rec.get_fields('001')[0].value()	# the local record number from the 001 (either the OCLC number or the partner's BSN)
	rec_analysis_msgs += 'Record '+rec_003_value+'_'+rec_001_value+'\n'
	
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
		rec_analysis_msgs += 'The 003 code - '+rec_003_value+' - did not match any of the partner institutions.\n'
		errors_found = True
	
	if rec_001_value.startswith('o'):	# this OCLC record did not get processed in step 4
		rec_analysis_msgs += '001/003 field values did not change to institutional code and BSN\n'
		for rec_035 in rec.get_fields('035'):
			rec_analysis_msgs += str(rec_035)+'\n'
		errors_found = True
	
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
	rec.add_field(new_008)
	
	# add the 006/007 format fields for electronic resource characteristics
	new_006 = Field(tag='006', data='m        d        ')
	rec.add_field(new_006)
	new_007 = Field(tag='007', data='cr cn |||m|||a')
	rec.add_field(new_007)
	
	# change byte 23 in the 008 field to code 'o' for 'online'
	rec_008_value = rec['008'].data
	rec['008'].data = rec_008_value[0:23] + 'o' + rec_008_value[24:]
	
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
		rda_rec = True
	else:
		rda_rec = False

	# create new 040 field for NNU
	for rec_040 in rec.get_fields('040'):
		rec.remove_field(rec_040)	# delete the existing 040 field(s)
	new_040 = Field(tag='040', indicators=[' ',' '], subfields=['a','NNU','b','eng','c','NNU'])
	if rda_rec:
		new_040.add_subfield('e','rda')
	rec.add_field(new_040)
	
	if rec.get_fields('049') > 0:
		rec.remove_field(rec.get_fields('049')[0])
	
	if len(rec.get_fields('050')) > 0:
		rec.get_fields('050')[0].indicators[0] = ' '
		rec.get_fields('050')[0].indicators[1] = '4'
		# THIS DOES NOT CHANGE THE INDICATORS - NOT SURE HOW TO DO SO
				
	if not rda_rec:
		# add GMD to 245$h for "[electronic resource]"
		for rec_245 in rec.get_fields('245'):
			rec_245.add_subfield('h', '[electronic resource]')
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
				
	new_500_aco = Field(tag='500', indicators=[' ',' '], subfields=['a','Part of the Arabic Collections Online (ACO) project, contributed by '+inst_name+'.'])
	rec.add_field(new_500_aco)
	
	if len(rec.get_fields('530')) > 0:
		for rec_530 in rec.get_fields('530'):
			rec.remove_field(rec_530)
	
	curr_year = datetime.date.today().year
	new_533 = Field(tag='533', indicators=[' ',' '], subfields=['a', 'Electronic reproduction.', 'b', 'New York, N.Y. :', 'c', 'New York University,', 'd', str(curr_year)+'.', '5', 'NNU'])
	rec.add_field(new_533)
	
	new_539 = Field(tag='539', indicators=[' ',' '], subfields=['a', 's', 'b', str(curr_year), 'd', 'nyu', 'e', 'n', 'g', 'o'])
	rec.add_field(new_539)
	
 	new_710 = Field(tag='710', indicators=['2',' '], subfields=['a', inst_710a, 'b', inst_710b])
 	rec.add_field(new_710)
	
	new_730 = Field(tag='730', indicators=['0',' '], subfields=['a','Arabic Collections Online.'])
	rec.add_field(new_730)
	
	new_776 = Field(tag='776', indicators=['0','8'], subfields=['i', 'Print version:'])
	
	# capture subfield data to insert into the new 776 field for the print version
	if len(rec.get_fields('100', '110')) > 0:
		new_776a = rec.get_fields('100', '110')[0].value()
		if new_776a.startswith('8'):
			new_776a = new_776a[7:]
		new_776.add_subfield('a', new_776a)
		
	new_776t = rec.get_fields('245')[0].get_subfields('a')[0]
	new_776t = new_776t.strip(' /:.,')
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
			rec_analysis_msgs += '020: '+str(rec_020)+'\n'
			if len(rec_020.get_subfields('a')) > 0:			# the 020 field has a subfield a
				for rec_020a in rec_020.get_subfields('a'):	# iterate through the subfield a's
					new_020z_field = Field(tag='020', indicators=[' ',' '], subfields=['z', rec_020a])
					new_020z_fields.append(new_020z_field)
					new_020z_subfields.append(rec_020a)
			rec.remove_field(rec_020)
	
	for new_020z_field in new_020z_fields:
		rec.add_field(new_020z_field)
	
	for new_776z in new_020z_subfields:
		new_776.add_subfield('z', new_776z)
	
	rec.add_field(new_776)
	
	if len(rec.get_fields('938')) > 0:
		for rec_938 in rec.get_fields('938'):
			rec.remove_field(rec_938)
	
	if len(rec.get_fields('994')) > 0:
		for rec_994 in rec.get_fields('994'):
			rec.remove_field(rec_994)
	
	rec_analysis_msgs += '-----------------------------------------------------------------\n'
	
	for orig_rec in orig_recs_all:
		orig_003_value = orig_rec.get_fields('003')[0].value()
		orig_001_value = orig_rec.get_fields('001')[0].value()
		if rec_003_value==orig_003_value and rec_001_value==orig_001_value:
			marcRecsOut_orig_recs_subset.write(orig_rec)
	
	return rec
	
######################################################################
##  Method:  insert_url()
######################################################################
def insert_url(rec):
	rec_003 = rec.get_fields('003')[0].value()
	rec_001 = rec.get_fields('001')[0].value()
	global handles_lines
	match = False
	
	for line in handles_lines:
		handle_data = line.split(",")
		handle_003 = handle_data[0]
		handle_001 = handle_data[1]
		handle = handle_data[2]
		print handle_003 + ", " + handle_001 + ", " + handle
		if rec_003 == handle_003 and rec_001 == handle_001:
			# add URL handle to the MARC record in an 856 $u field
			new_856 = Field(tag='856', indicators=['4','0'], subfields=['u',handle])
			rec.add_field(new_856)
			
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
			rec.add_field(new_959)
			
			match = True
	
	return rec

######################################################################
##  MAIN SCRIPT
######################################################################
rec_count = 0

for record in marcRecsIn_script:	# Iterate through all records in marcRecsIn
	rec_converted = convert_eres_rec(record)
	# rec_converted = insert_url(record)
	
	rec_count +=1
	
	marcRecsOut_final.write(rec_converted)

# NEED TO ADD CODE FOR PROCESSING FILE marcRecsIn_script_added

rec_analysis_msgs += 'Total records processed for '+folder_name+': '+str(rec_count)+' records\n'
rec_analysis_txt.write(rec_analysis_msgs)
print str(rec_count)+" records were processed in file"
print 'subset of original records = '+str(orig_subset_count)+' records'

# handles_csv.close()
marcRecsOut_final.close()
marcRecsOut_orig_recs_subset.close()
rec_analysis_txt.close()
