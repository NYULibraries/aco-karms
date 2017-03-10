#!/usr/bin/python

import os
import errno
import sys
import time
import shutil
import codecs
import pymarc
from pymarc import Record, Field
import aco_globals
import aco_functions

inst_code = raw_input('Enter the institutional code: ')
batch_date = raw_input('Enter the batch date (YYYYMMDD): ')
batch_name = inst_code+'_'+batch_date
aco_globals.batch_folder += '/'+inst_code+'/'+batch_name

# Check if records have been processed before by this script
prev_processed = os.path.exists(aco_globals.batch_folder+'/'+batch_name+'_3')

input_files = {}
if not prev_processed or inst_code == 'NNU':
	# Get INPUT FILES from folder 'batch_name_1'
	input_folder = aco_globals.batch_folder+'/'+batch_name+'_1'
	
	# retrieve the ORIGINAL records that DO NOT have a corresponding OCLC record
	try:
		marcRecsIn_orig_no_oclc = pymarc.MARCReader(file(input_folder+'/'+batch_name+'_1_orig_no_oclc_nums.mrc'), to_unicode=True, force_utf8=True)
		input_files['orig_no_oclc'] = [marcRecsIn_orig_no_oclc, batch_name+'_1/'+batch_name+'_1_orig_no_oclc_nums.mrc', 'orig']
	except:	marcRecsIn_orig_no_oclc = ''
	
	# retrieve the ORIGINAL records that DO have a corresponding OCLC record
	try:
		marcRecsIn_orig_with_oclc = pymarc.MARCReader(file(input_folder+'/'+batch_name+'_1_orig_with_oclc_nums.mrc'), to_unicode=True, force_utf8=True)
		input_files['orig_with_oclc'] = [marcRecsIn_orig_with_oclc, batch_name+'_1/'+batch_name+'_1_orig_with_oclc_nums.mrc', 'orig']
	except:	marcRecsIn_orig_with_oclc = ''
	
	# retrieve the OCLC records from the BATCH EXPORT process (for non-NYU records)
	try:
		marcRecsIn_oclc_batch = pymarc.MARCReader(file(aco_globals.batch_folder+'/'+batch_name+'_2_oclc_recs_batch.mrc'), to_unicode=True, force_utf8=True)
		input_files['oclc_batch'] = [marcRecsIn_oclc_batch, batch_name+'_2_oclc_recs_batch.mrc', 'oclc']
	except: marcRecsIn_oclc_batch = ''
		
	## retreive the OCLC records from the MANUAL process - OBSOLETE?  These would be records manually found in OCLC Connexion for original records lacking OCLC nums 
	#try:	marcRecsIn_oclc_manual = pymarc.MARCReader(file(aco_globals.batch_folder+'/'+inst_code+'_'+batch_date+'_3_oclc_recs_manual.mrc'), to_unicode=True, force_utf8=True)
	#except:	marcRecsIn_oclc_manual = ''
	## compile the list of 001s/003s and OCLC nums for the OCLC MANUAL records
	#try:
	#	oclc_nums_bsns_manual = open(aco_globals.batch_folder+'/'+inst_code+'_'+batch_date+'_3_oclc_nums_bsns_manual.txt', 'r')	# opens the txt file containing the 001s, 003s, and corresponding OCLC nums (read-only)
	#	oclc_nums_bsns_manual_lines = oclc_nums_bsns_manual.readlines()	# read the txt file containing 001/003 and corresponding OCLC numbers
	#	for line in oclc_nums_bsns_manual_lines:
	#		aco_globals.oclc_nums_bsns_all.append(line)
	#	oclc_nums_bsns_manual.close()
	#except:
	#	oclc_nums_bsns_manual_lines = ''

else:
	# Get INPUT FILES from folder 'batch_name_3'
	input_folder = aco_globals.batch_folder+'/'+batch_name+'_3'
	
	# retrieve the UPDATED records from the manual QC process
	try:
		marcRecsIn_updates = pymarc.MARCReader(file(input_folder+'/'+batch_name+'_3_updates.mrc'), to_unicode=True, force_utf8=True)
		input_files['updates'] = [marcRecsIn_updates, batch_name+'_3/'+batch_name+'_3_updates.mrc', 'oclc']
	except:	marcRecsIn_updates = ''
	
	# retrieve the subset of FINAL records from the previous run of this script
	try:	marcRecsIn_final_subset = pymarc.MARCReader(file(input_folder+'/'+batch_name+'_3_final_recs.mrc'), to_unicode=True, force_utf8=True)
	except:	marcRecsIn_final_subset = ''


# compile the list of 001s/003s and OCLC nums for the OCLC BATCH EXPORT records
try:
	orig_with_oclc_nums_txt = codecs.open(aco_globals.batch_folder+'/'+batch_name+'_1/'+batch_name+'_1_orig_with_oclc_nums.txt', 'r')	# opens the txt file containing the 001s, 003s, and corresponding OCLC nums (read-only)
	orig_with_oclc_nums_lines = orig_with_oclc_nums_txt.readlines()		# read the txt file containing 001/003 and corresponding OCLC numbers
	for line in orig_with_oclc_nums_lines:
		aco_globals.oclc_nums_bsns_all.append(line)
	orig_with_oclc_nums_txt.close()
except:
	orig_with_oclc_nums_lines = ''


if prev_processed:
	# Move previously processed output files to timestamped folder
	prev_file_timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime(os.path.getmtime(aco_globals.batch_folder+'/'+batch_name+'_3/'+batch_name+'_3_final_recs.mrc')))
	dest_folder = aco_globals.batch_folder+'/'+batch_name+'_3_'+prev_file_timestamp+'/'
	src_folder = aco_globals.batch_folder+'/'
	src_3 = batch_name+'_3/'
	src_4 = batch_name+'_4_final_recs.mrc'
	src_dirs = [src_3, src_4]	
	for src in src_dirs:
		if os.path.exists(src_folder+src):
			shutil.move(src_folder+src, dest_folder+src)


# retrieve the CSV file containing the 003/001 values and corresponding URL handles
try:
	handles_csv = open(aco_globals.batch_folder+'/handles.csv', 'r')
	aco_globals.handles_lines = handles_csv.readlines()
	handles_csv.close()
except:	handles_csv = ''

# retrieve the CSV file containing the BSNs and source entity (SE) book numbers
try:
	bsn_se_csv = open(aco_globals.batch_folder+'/bsn-se-map.csv', 'r')
	aco_globals.bsn_se_lines = bsn_se_csv.readlines()
	bsn_se_csv.close()
except:	bsn_se_csv = ''

# OUTPUT FILES
output_folder = aco_globals.batch_folder+'/'+batch_name+'_3'

try:
	os.makedirs(output_folder+'/'+batch_name+'_3_errors_no_880s/')
	os.makedirs(output_folder+'/'+batch_name+'_3_errors_missing_key_880s/')
	os.makedirs(output_folder+'/'+batch_name+'_3_errors_unlinked_880s/')
	os.makedirs(output_folder+'/'+batch_name+'_3_errors_series/')
	os.makedirs(output_folder+'/'+batch_name+'_3_errors_misc/')
except OSError as exception:
	if exception.errno != errno.EEXIST:
		raise

aco_globals.marcRecsOut_no_880s = pymarc.MARCWriter(file(output_folder+'/'+batch_name+'_3_errors_no_880s/'+batch_name+'_3_no_880s.mrc', 'w'))
aco_globals.recs_no_880s_txt = codecs.open(output_folder+'/'+batch_name+'_3_errors_no_880s/'+batch_name+'_3_no_880s.txt', 'w', encoding='utf8')
aco_globals.recs_no_880s_txt.write('Records with NO 880 script fields - batch '+batch_name+'\n')
aco_globals.recs_no_880s_txt.write('--  These records do NOT contain ANY 880 script fields\n')
aco_globals.recs_no_880s_txt.write('Report produced: '+aco_globals.curr_time+'\n')

aco_globals.marcRecsOut_missing_key_880s = pymarc.MARCWriter(file(output_folder+'/'+batch_name+'_3_errors_missing_key_880s/'+batch_name+'_3_missing_key_880s.mrc', 'w'))
aco_globals.recs_missing_key_880s_txt = codecs.open(output_folder+'/'+batch_name+'_3_errors_missing_key_880s/'+batch_name+'_3_missing_key_880s.txt', 'w', encoding='utf8')
aco_globals.recs_missing_key_880s_txt.write('Records MISSING KEY 880 script fields - batch '+batch_name+'\n')
aco_globals.recs_missing_key_880s_txt.write('--  At least one of the key fields is missing subfield $6,\n')
aco_globals.recs_missing_key_880s_txt.write('    so the corresponding 880 script field is missing or unlinked\n')
aco_globals.recs_missing_key_880s_txt.write('--  Key fields:\n    100, 110, 111, 130\n    240, 245, 246, 250, 260, 264\n    440, 490\n    700, 710, 711, 730\n    800, 810, 811, 830\n')
aco_globals.recs_missing_key_880s_txt.write('Report produced: '+aco_globals.curr_time+'\n')

aco_globals.marcRecsOut_unlinked_880s = pymarc.MARCWriter(file(output_folder+'/'+batch_name+'_3_errors_unlinked_880s/'+batch_name+'_3_unlinked_880s.mrc', 'w'))
aco_globals.recs_unlinked_880s_txt = codecs.open(output_folder+'/'+batch_name+'_3_errors_unlinked_880s/'+batch_name+'_3_unlinked_880s.txt', 'w', encoding='utf8')
aco_globals.recs_unlinked_880s_txt.write('Records containing UNLINKED 880 script fields - batch '+batch_name+'\n')
aco_globals.recs_unlinked_880s_txt.write('--  At least one 880 field has sequence number -00 in subfield $6,\n')
aco_globals.recs_unlinked_880s_txt.write('    meaning it is not linked to the corresponding parallel field\n')
aco_globals.recs_unlinked_880s_txt.write('Report produced: '+aco_globals.curr_time+'\n')

aco_globals.marcRecsOut_series_errors = pymarc.MARCWriter(file(output_folder+'/'+batch_name+'_3_errors_series/'+batch_name+'_3_series_errors.mrc', 'w'))
aco_globals.recs_series_errors_txt = codecs.open(output_folder+'/'+batch_name+'_3_errors_series/'+batch_name+'_3_series_errors.txt', 'w', encoding='utf8')
aco_globals.recs_series_errors_txt.write('Records containing SERIES errors - batch '+batch_name+'\n')
aco_globals.recs_series_errors_txt.write('--  These records contain an error with series headings in the 490/800/810/811/830 fields\n')
aco_globals.recs_series_errors_txt.write('--  Either the 490 field has 1st indicator=0 (untraced)\n')
aco_globals.recs_series_errors_txt.write('--  Or there are more 490 fields than there are 800/810/811/830 fields,\n')
aco_globals.recs_series_errors_txt.write('    so the corresponding 8XX heading needs added\n')
aco_globals.recs_series_errors_txt.write('Report produced: '+aco_globals.curr_time+'\n')

aco_globals.marcRecsOut_misc_errors = pymarc.MARCWriter(file(output_folder+'/'+batch_name+'_3_errors_misc/'+batch_name+'_3_misc_errors.mrc', 'w'))
aco_globals.recs_misc_errors_txt = codecs.open(output_folder+'/'+batch_name+'_3_errors_misc/'+batch_name+'_3_misc_errors.txt', 'w', encoding='utf8')
aco_globals.recs_misc_errors_txt.write('Records containing MISCELLANEOUS errors - batch '+batch_name+'\n')
aco_globals.recs_misc_errors_txt.write('--  Each of these records contain at least one of the miscellaneous errors\n')
aco_globals.recs_misc_errors_txt.write('    recorded mostly for notice of validation errors or to identify programming issues\n')
aco_globals.recs_misc_errors_txt.write('--  List of possible miscellaneous errors:\n')
aco_globals.recs_misc_errors_txt.write('    --  the OCLC # in the OCLC batch record did not match on any OCLC #s in the original records\n')
aco_globals.recs_misc_errors_txt.write('    --  record contains multiple 999 fields\n')
aco_globals.recs_misc_errors_txt.write('    --  zero or multiple $6 subfields in 880s\n')
aco_globals.recs_misc_errors_txt.write('    --  record is missing an 040 field\n')
aco_globals.recs_misc_errors_txt.write('    --  record contains invalid replacement character (black diamond with question mark) - found in NYU records\n')
aco_globals.recs_misc_errors_txt.write('    --  code in the 003 does not match any of the partner institution codes\n')
aco_globals.recs_misc_errors_txt.write('    --  the 003/001 fields did not change from the OCLC # to the BSN during processing\n')
aco_globals.recs_misc_errors_txt.write('    --  the 003/001 fields in the handles.csv file did not match on any record in the batch\n')
aco_globals.recs_misc_errors_txt.write('    --  an 006 or 007 field is present in the original record (signifying an alternate format other than print)\n')
aco_globals.recs_misc_errors_txt.write('    --  record is missing a 245 title field, or has multiple 245 fields\n')
aco_globals.recs_misc_errors_txt.write('    --  a 245 $h GMD field is present in the original record (signifying an alternate format other than print)\n')
aco_globals.recs_misc_errors_txt.write('    --  the 245 $h GMD field was not added to a non-RDA e-version record during processing\n')
aco_globals.recs_misc_errors_txt.write('    --  the $6 subfield did not sort to the first position in the field - issue with NYU records\n')
aco_globals.recs_misc_errors_txt.write('    --  record is missing a call number - no 050 or 090 field\n')
aco_globals.recs_misc_errors_txt.write('Report produced: '+aco_globals.curr_time+'\n')

aco_globals.marcRecsOut_errors_all = pymarc.MARCWriter(file(output_folder+'/'+batch_name+'_3_errors_all.mrc', 'w'))
aco_globals.recs_errors_all_txt = codecs.open(output_folder+'/'+batch_name+'_3_errors_all.txt', 'w', encoding='utf8')
aco_globals.recs_errors_all_txt.write('ALL Records containing any type of error - batch '+batch_name+'\n')
aco_globals.recs_errors_all_txt.write('--  Each of these records have one or more of the following errors:\n')
aco_globals.recs_errors_all_txt.write('    --  no 880 fields\n')
aco_globals.recs_errors_all_txt.write('    --  missing a key 880 field\n')
aco_globals.recs_errors_all_txt.write('    --  have an unlinked 880 field\n')
aco_globals.recs_errors_all_txt.write('    --  have a series heading error in the 490/800/810/811/830 fields\n')
aco_globals.recs_errors_all_txt.write('    --  have one of the various miscellaneous errors, marked with ERROR-MISC\n')
aco_globals.recs_errors_all_txt.write('    --  missing a call number - no 050 or 090 field\n')
aco_globals.recs_errors_all_txt.write('Report produced: '+aco_globals.curr_time+'\n')

all_recs_analysis_txt = codecs.open(output_folder+'/'+batch_name+'_3_all_recs_analysis.txt', 'w', encoding='utf8')

aco_globals.marcRecsOut_final_subset = pymarc.MARCWriter(file(output_folder+'/'+batch_name+'_3_final_recs.mrc', 'w'))
aco_globals.marcRecsOut_final_all = pymarc.MARCWriter(file(aco_globals.batch_folder+'/'+batch_name+'_4_final_recs.mrc', 'w'))

if 'updates' in input_files:
	# Write out subset of FINAL records from previous output
	for final_rec in marcRecsIn_final_subset:
		aco_globals.recs_final_prev_subset_count += 1
		aco_globals.marcRecsOut_final_subset.write(final_rec)
		aco_globals.marcRecsOut_final_all.write(final_rec)
		rda_rec, msg = aco_functions.check_if_rda(final_rec)
		if rda_rec:
			aco_globals.recs_rda_count += 1

def write_filename(filename):
	aco_globals.recs_no_880s_txt.write('---------------------------------------------------------------------\nFILE: '+filename+'\n---------------------------------------------------------------------\n')
	aco_globals.recs_missing_key_880s_txt.write('---------------------------------------------------------------------\nFILE: '+filename+'\n---------------------------------------------------------------------\n')
	aco_globals.recs_unlinked_880s_txt.write('---------------------------------------------------------------------\nFILE: '+filename+'\n---------------------------------------------------------------------\n')
	aco_globals.recs_series_errors_txt.write('---------------------------------------------------------------------\nFILE: '+filename+'\n---------------------------------------------------------------------\n')
	aco_globals.recs_misc_errors_txt.write('---------------------------------------------------------------------\nFILE: '+filename+'\n---------------------------------------------------------------------\n')
	aco_globals.recs_errors_all_txt.write('---------------------------------------------------------------------\nFILE: '+filename+'\n---------------------------------------------------------------------\n')


# MAIN PROCESSING AND STATISTICS ANALYSIS
if 'oclc_batch' in input_files:
	orig_with_oclc_key = input_files.pop('orig_with_oclc', None)

rec_count_tot = 0
input_file_msg = ''
for file_type in input_files:
	mrc_file = input_files[file_type][0]
	filename = input_files[file_type][1]
	rec_type = input_files[file_type][2]
	write_filename(filename)
	rec_count_file = 0
	for mrc_rec in mrc_file:
		dup_rec = aco_functions.process_rec(mrc_rec, rec_type)
		if not dup_rec:
			rec_count_file +=1
			rec_count_tot +=1
	input_file_msg += 'Input File ('+file_type+'): '+str(rec_count_file)+'\n'
	if file_type == 'updates':
		input_file_msg += 'Input File (final subset): '+str(aco_globals.recs_final_prev_subset_count)+'\n'
		rec_count_tot += aco_globals.recs_final_prev_subset_count


aco_globals.recs_no_880s_txt.write('TOTAL Number of Records with NO 880 script fields: '+str(aco_globals.recs_no_880s_count)+'\n\n')
aco_globals.recs_missing_key_880s_txt.write('TOTAL Number of Records missing key 880 script fields: '+str(aco_globals.recs_missing_key_880s_count)+'\n\n')
aco_globals.recs_unlinked_880s_txt.write('TOTAL Number of Records containing unlinked 880 script fields: '+str(aco_globals.recs_unlinked_880s_count)+'\n\n')
aco_globals.recs_series_errors_txt.write('TOTAL Number of Records containing series errors: '+str(aco_globals.recs_series_errors_count)+'\n\n')
aco_globals.recs_misc_errors_txt.write('TOTAL Number of Records containing miscellaneous errors: '+str(aco_globals.recs_misc_errors_count)+'\n\n')
aco_globals.recs_errors_all_txt.write('TOTAL Number of Records containing any type of error: '+str(aco_globals.recs_errors_all_count)+'\n\n')

aco_globals.all_recs_analysis_msg += 'Total records processed - batch '+batch_name+': '+str(rec_count_tot)+' records\n'
aco_globals.all_recs_analysis_msg += 'Report produced: '+aco_globals.curr_time+'\n'
aco_globals.all_recs_analysis_msg += input_file_msg + '\n'

aco_globals.recs_final_curr_subset_count = aco_globals.recs_final_prev_subset_count + aco_globals.recs_final_this_subset_count

perc_errors_all = aco_functions.calculate_percentage(aco_globals.recs_errors_all_count,rec_count_tot)
perc_final_recs = aco_functions.calculate_percentage(aco_globals.recs_final_curr_subset_count,rec_count_tot)
perc_880s = aco_functions.calculate_percentage(aco_globals.recs_880s_count,rec_count_tot)
perc_no_880s = aco_functions.calculate_percentage(aco_globals.recs_no_880s_count,rec_count_tot)
perc_missing_key_880s = aco_functions.calculate_percentage(aco_globals.recs_missing_key_880s_count,rec_count_tot)
perc_unlinked_880s = aco_functions.calculate_percentage(aco_globals.recs_unlinked_880s_count,rec_count_tot)
perc_series_errors = aco_functions.calculate_percentage(aco_globals.recs_series_errors_count,rec_count_tot)
perc_misc_errors = aco_functions.calculate_percentage(aco_globals.recs_misc_errors_count,rec_count_tot)
perc_rda = aco_functions.calculate_percentage(aco_globals.recs_rda_count,rec_count_tot)
perc_no_call_num = aco_functions.calculate_percentage(aco_globals.recs_no_call_num_count,rec_count_tot)

aco_globals.all_recs_analysis_msg += 'Records where OCLC nums did not match: '+str(aco_globals.recs_no_oclc_match_count)+'\n'
aco_globals.all_recs_analysis_msg += 'Total records containing any type of error for this round: '+str(aco_globals.recs_errors_all_count)+' ('+perc_errors_all+'%)\n'
aco_globals.all_recs_analysis_msg += 'Total records passing to final version for this round: '+str(aco_globals.recs_final_curr_subset_count)+' ('+perc_final_recs+'%)\n'
aco_globals.all_recs_analysis_msg += '-----------------------\n'
aco_globals.all_recs_analysis_msg += 'Records containing 880 script fields: '+str(aco_globals.recs_880s_count)+' ('+perc_880s+'%)\n'
aco_globals.all_recs_analysis_msg += 'Records with NO 880 script fields: '+str(aco_globals.recs_no_880s_count)+' ('+perc_no_880s+'%)\n'
aco_globals.all_recs_analysis_msg += 'Records missing key 880 script fields: '+str(aco_globals.recs_missing_key_880s_count)+' ('+perc_missing_key_880s+'%)\n'
aco_globals.all_recs_analysis_msg += 'Records containing unlinked 880 script fields: '+str(aco_globals.recs_unlinked_880s_count)+' ('+perc_unlinked_880s+'%)\n'
aco_globals.all_recs_analysis_msg += 'Records containing series errors in 490/800/810/811/830 fields: '+str(aco_globals.recs_series_errors_count)+' ('+perc_series_errors+'%)\n'
aco_globals.all_recs_analysis_msg += 'Records containing miscellaneous errors: '+str(aco_globals.recs_misc_errors_count)+' ('+perc_misc_errors+'%)\n'
aco_globals.all_recs_analysis_msg += 'Records containing bad encoding replacement character: '+str(aco_globals.recs_repl_char_count)+'\n'
aco_globals.all_recs_analysis_msg += 'Records containing RDA fields: '+str(aco_globals.recs_rda_count)+' ('+perc_rda+'%)\n'
aco_globals.all_recs_analysis_msg += 'Records with NO 050 or 090 call number fields: '+str(aco_globals.recs_no_call_num_count)+' ('+perc_no_call_num+'%)\n'
aco_globals.all_recs_analysis_msg += '---------------------------------------------------------------------\nINDIVIDUAL RECORDS ANALYSIS:\n---------------------------------------------------------------------\n'

all_recs_analysis_txt.write(aco_globals.all_recs_analysis_msg)
all_recs_analysis_txt.write(aco_globals.indiv_rec_analysis_msgs)
print str(rec_count_tot)+' records were processed in all input files'

aco_globals.marcRecsOut_no_880s.close()
aco_globals.recs_no_880s_txt.close()

aco_globals.marcRecsOut_missing_key_880s.close()
aco_globals.recs_missing_key_880s_txt.close()

aco_globals.marcRecsOut_unlinked_880s.close()
aco_globals.recs_unlinked_880s_txt.close()

aco_globals.marcRecsOut_series_errors.close()
aco_globals.recs_series_errors_txt.close()

aco_globals.marcRecsOut_misc_errors.close()
aco_globals.recs_misc_errors_txt.close()

aco_globals.marcRecsOut_errors_all.close()
aco_globals.recs_errors_all_txt.close()

all_recs_analysis_txt.close()
aco_globals.marcRecsOut_final_subset.close()
aco_globals.marcRecsOut_final_all.close()

