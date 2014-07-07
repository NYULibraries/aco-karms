#!/usr/bin/python

import os
import errno
import pymarc
from pymarc import Record, Field
import codecs
import aco_functions

parent_dir = os.path.dirname(os.getcwd())
work_folder = parent_dir+'/work'
inst_code = raw_input('Enter the 3-letter institutional code: ')
batch_date = raw_input('Enter the batch date (YYYYMMDD): ')
batch_folder = work_folder+'/'+inst_code+'/'+inst_code+'_'+batch_date

# INPUT FILES
oclc_nums_bsns_all = []

# retrieve the ORIGINAL records that DO NOT have a corresponding OCLC record
try:	marcRecsIn_orig_recs_no_oclc = pymarc.MARCReader(file(batch_folder+'/'+inst_code+'_'+batch_date+'_2_orig_recs_no_oclc_nums.mrc'), to_unicode=True, force_utf8=True)
except:	marcRecsIn_orig_recs_no_oclc = ''

# retrieve the OCLC records from the BATCH process
try:	marcRecsIn_oclc_batch = pymarc.MARCReader(file(batch_folder+'/'+inst_code+'_'+batch_date+'_3_oclc_recs_batch.mrc'), to_unicode=True, force_utf8=True)
except: marcRecsIn_oclc_batch = ''
try:
	oclc_nums_bsns_batch = open(batch_folder+'/'+inst_code+'_'+batch_date+'_2_oclc_nums_bsns_batch.txt', 'r')	# opens the txt file containing the 001s, 003s, and corresponding OCLC nums (read-only)
	oclc_nums_bsns_batch_lines = oclc_nums_bsns_batch.readlines()	# read the txt file containing 001/003 and corresponding OCLC numbers
	for line in oclc_nums_bsns_batch_lines:
		oclc_nums_bsns_all.append(line)
	oclc_nums_bsns_batch.close()
except:
	oclc_nums_bsns_batch_lines = ''

# retreive the OCLC records from the MANUAL process
try:	marcRecsIn_oclc_manual = pymarc.MARCReader(file(batch_folder+'/'+inst_code+'_'+batch_date+'_3_oclc_recs_manual.mrc'), to_unicode=True, force_utf8=True)
except:	marcRecsIn_oclc_manual = ''
try:
	oclc_nums_bsns_manual = open(batch_folder+'/'+inst_code+'_'+batch_date+'_3_oclc_nums_bsns_manual.txt', 'r')	# opens the txt file containing the 001s, 003s, and corresponding OCLC nums (read-only)
	oclc_nums_bsns_manual_lines = oclc_nums_bsns_manual.readlines()	# read the txt file containing 001/003 and corresponding OCLC numbers
	for line in oclc_nums_bsns_manual_lines:
		oclc_nums_bsns_all.append(line)
	oclc_nums_bsns_manual.close()
except:
	oclc_nums_bsns_manual_lines = ''

# retrieve the CSV file containing the 003/001 values and corresponding URL handles
try:
	handles = open(batch_folder+'/handles.csv', 'r')
	handles_lines = handles.readlines()
	handles.close()
except:	handles = ''

# OUTPUT FILES
marcRecsOut_no_script = pymarc.MARCWriter(file(batch_folder+'/'+inst_code+'_'+batch_date+'_4_recs_no_script.mrc', 'w'))
recs_no_script = codecs.open(batch_folder+'/'+inst_code+'_'+batch_date+'_4_recs_no_script_nums.txt', 'w')
recs_no_script.write('Records LACKING 880 script fields:\n-------------------------------------------------------------\n')

marcRecsOut_final = pymarc.MARCWriter(file(batch_folder+'/'+inst_code+'_'+batch_date+'_4_dlts_final_recs.mrc', 'w'))

rec_analysis_txt = codecs.open(batch_folder+'/'+inst_code+'_'+batch_date+'_4_rec_analysis.txt', 'w')
indiv_rec_analysis_msg = ''
all_rec_analysis_msg = ''


oclc_nums = set()			# variable to keep track of oclc numbers processed
rec_count_tot = 0			# variable to keep track of the total number of records processed
rec_count_file1 = 0			# variable to keep track of the number of records processed for File 1
rec_count_file2 = 0			# variable to keep track of the number of records processed for File 2
rec_count_file3 = 0			# variable to keep track of the number of records processed for File 3
rec_no_oclc_match_count = 0	# variable to keep track of the number of OCLC records that did not match an original record
recs_880s_count = 0			# variable to keep track of the number of records having 880 script fields
recs_no_880s_count = 0		# variable to keep track of the number of records NOT having 880 script fields
recs_rda_count = 0			# variable to keep track of the number of records having RDA 3XX or 040e fields
recs_repl_char_count = 0	# variable to keep track of the number of records containing the bad encoding replacement character

######################################################################
##  Method process_rec()
######################################################################
def process_rec(rec, type):
	global oclc_nums
	global oclc_nums_bsns_all
	global handles_lines
	global rec_no_oclc_match_count
	global recs_880s_count
	global recs_no_880s_count
	global recs_rda_count
	global recs_repl_char_count
	global rec_count_tot
	global indiv_rec_analysis_msg
	
	rec_003_value = rec.get_fields('003')[0].value()	# either 'OCLC' or the partner's institution code from the 003 field
	rec_001_value = rec.get_fields('001')[0].value()	# either the OCLC number or the inst_id from the 001 field
	if type=='oclc':
		################################################
		# Check for duplicate OCLC record
		dup_num = False
		for num in oclc_nums:
			if rec_001_value == num:
				dup_num = True
		if not dup_num:
			oclc_nums.add(rec_001_value)
		
	if type=='orig' or not dup_num:
		################################################
		# Add institutional code and record ID to OCLC records, etc.
		rec, oclc_id, inst_id, oclc_match, msg_1 = aco_functions.process_001_003_fields(rec, oclc_nums_bsns_all)
		indiv_rec_analysis_msg += msg_1
		if not oclc_match:
			rec_no_oclc_match_count += 1
		
		################################################
		# Check if record contains 880 script fields
		script_rec, msg_2 = aco_functions.check_880s(rec)
		indiv_rec_analysis_msg += msg_2
		if not script_rec:
			marcRecsOut_no_script.write(rec)
			recs_no_script.write('   OCLC ID: '+oclc_id+' / Institution ID: '+inst_id+'\n')
			recs_no_880s_count += 1
		else:
			recs_880s_count += 1
			
		################################################
		# Check if record contains RDA fields
		rda_rec, msg_3 = aco_functions.check_rda(rec)
		indiv_rec_analysis_msg += msg_3
		if rda_rec:
			recs_rda_count += 1
		
		################################################
		# Check if record contains bad encoding script character (black diamond around question-mark)
		# Evidenced by presence of Python source code u"\uFFFD" (See: http://www.fileformat.info/info/unicode/char/0fffd/index.htm)
		repl_char, msg_4 = aco_functions.check_repl_char(rec)
		indiv_rec_analysis_msg += msg_4
		if repl_char:
			recs_repl_char_count += 1
		
		################################################
		# Add/Delete/Modify MARC fields in print record to convert to an e-resource record
		rec, msg_5 = aco_functions.convert_2_eres_rec(rec, rda_rec)
		indiv_rec_analysis_msg += msg_5
		
		################################################
		# Sort any $6 subfields that do not appear first in the field
		rec = aco_functions.sort_6_subs(rec)
		
		aco_functions.second_sort_6_check(rec)
		
		################################################
		# Link any unlinked 880 fields (having "00" in the 880 $6 numbering)
		rec, unlinked_exist, msg_6 = aco_functions.link_880s(rec)
		indiv_rec_analysis_msg += msg_6
		
		################################################
		# Match the 001/003 fields and insert the corresponding URL handle in an 856 field
		rec, msg_7 = aco_functions.insert_url(rec, handles_lines)
		indiv_rec_analysis_msg += msg_7
		
		indiv_rec_analysis_msg += '-------------------------------------------------\n'
		
		################################################
		# Change LDR values
		ldr = list(rec.leader)
		ldr[5] = 'n'
		ldr[6] = 'a'
		ldr[7] = 'm'
		#ldr[9] = 'a'
		rec.leader = ''.join(ldr)
		
		################################################
		# Write out individual .mrc record
		try: os.makedirs(batch_folder+'/mrc_out')
		except OSError as exception:
			if exception.errno != errno.EEXIST:
				raise
		indiv_marcRecOut = pymarc.MARCWriter(file(batch_folder+'/mrc_out/'+inst_id+'_mrc.mrc', 'w'))
		indiv_marcRecOut.write(rec)
		indiv_marcRecOut.close()
		
		################################################
		# Convert MARC to MARCXML and write out individual MARCXML record
		rec_xml = pymarc.record_to_xml(rec, namespace=True)
		try: os.makedirs(batch_folder+'/marcxml_out')
		except OSError as exception:
			if exception.errno != errno.EEXIST:
				raise
		indiv_marcRecOut_xml = codecs.open(batch_folder+'/marcxml_out/'+inst_id+'_marcxml.xml', 'w')
		indiv_marcRecOut_xml.write(rec_xml)
		indiv_marcRecOut_xml.close()
		
		################################################
		# Write out record to full set of final records
		marcRecsOut_final.write(rec)
		
		rec_count_tot +=1


recs_no_script.write('\nFile: 2_orig_recs_no_oclc_nums.mrc\n')
for record_orig in marcRecsIn_orig_recs_no_oclc:
	process_rec(record_orig, 'orig')
	rec_count_file1 +=1

recs_no_script.write('File: 3_oclc_recs_batch.mrc\n')
for record_oclc_1 in marcRecsIn_oclc_batch:
	process_rec(record_oclc_1, 'oclc')
	rec_count_file2 +=1

recs_no_script.write('\nFile: 3_oclc_recs_manual.mrc\n')
for record_oclc_2 in marcRecsIn_oclc_manual:
	process_rec(record_oclc_2, 'oclc')
	rec_count_file3 +=1

recs_no_script.write('-------------------------------------------------------------\n')
recs_no_script.write('TOTAL Number of Records LACKING 880 script fields: '+str(recs_no_880s_count))

all_rec_analysis_msg += 'Total records processed for '+inst_code+'_'+batch_date+': '+str(rec_count_tot)+' records\n'
all_rec_analysis_msg += 'File 1 (orig-no oclc num): '+str(rec_count_file1)+'\n'
all_rec_analysis_msg += 'File 2 (oclc-batch): '+str(rec_count_file2)+'\n'
all_rec_analysis_msg += 'File 3 (oclc-manual): '+str(rec_count_file3)+'\n\n'

perc_880s = aco_functions.calculate_percentage(recs_880s_count,rec_count_tot)
perc_no_880s = aco_functions.calculate_percentage(recs_no_880s_count,rec_count_tot)
perc_rda = aco_functions.calculate_percentage(recs_rda_count,rec_count_tot)
all_rec_analysis_msg += 'Records where OCLC nums did not match: '+str(rec_no_oclc_match_count)+'\n'
all_rec_analysis_msg += 'Records containing 880 script fields: '+str(recs_880s_count)+' ('+perc_880s+'%)\n'
all_rec_analysis_msg += 'Records NOT containing 880 script fields: '+str(recs_no_880s_count)+' ('+perc_no_880s+'%)\n'
all_rec_analysis_msg += 'Records containing RDA fields: '+str(recs_rda_count)+' ('+perc_rda+'%)\n'
all_rec_analysis_msg += 'Records containing bad encoding replacement character: '+str(recs_repl_char_count)+'\n'
all_rec_analysis_msg += '-------------------------------------------------\nINDIVIDUAL RECORDS ANALYSIS:\n-------------------------------------------------\n'

rec_analysis_txt.write(all_rec_analysis_msg)
rec_analysis_txt.write(indiv_rec_analysis_msg)
print str(rec_count_tot)+' records were processed in all files'

marcRecsOut_no_script.close()
recs_no_script.close()
marcRecsOut_final.close()
rec_analysis_txt.close()
