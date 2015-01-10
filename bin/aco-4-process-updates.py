#!/usr/bin/python

import os
import errno
import pymarc
from pymarc import Record, Field
import codecs
import datetime
import aco_globals
import aco_functions

inst_code = raw_input('Enter the 3-letter institutional code: ')
batch_date = raw_input('Enter the batch date (YYYYMMDD): ')
batch_name = inst_code+'_'+batch_date
aco_globals.batch_folder += '/'+inst_code+'/'+batch_name

curr_upd_num = raw_input('Enter the number for this round of updates: ')
prev_upd_num = int(curr_upd_num)-1
if prev_upd_num == 0:
	upd_input_folder = aco_globals.batch_folder+'/'+batch_name+'_3_new'
else:
	upd_input_folder = aco_globals.batch_folder+'/'+batch_name+'_4_updates_'+str(prev_upd_num)

upd_output_folder = aco_globals.batch_folder+'/'+batch_name+'_4_updates_'+curr_upd_num

# INPUT FILES
updates_filename = ''
if prev_upd_num == 0:
	# retrieve the UPDATED records from the NEW processing
	try:
		marcRecsIn_updates = pymarc.MARCReader(file(aco_globals.batch_folder+'/'+batch_name+'_3_updates.mrc'), to_unicode=True, force_utf8=True)
		updates_filename = batch_name+'_3_updates.mrc'
	except:	marcRecsIn_updates = ''
	
else:
	# retrieve the UPDATED records from the UPDATES processing
	try:
		marcRecsIn_updates = pymarc.MARCReader(file(upd_input_folder+'.mrc'), to_unicode=True, force_utf8=True)
		updates_filename = batch_name+'_4_updates_'+str(prev_upd_num)+'.mrc'
	except:	marcRecsIn_updates = ''
	
# retrieve the subset of FINAL records that passed checks from the previous round of processing
try:	marcRecsIn_final_rnd = pymarc.MARCReader(file(upd_input_folder+'/'+batch_name+'_5_final_recs.mrc'), to_unicode=True, force_utf8=True)
except: marcRecsIn_final_rnd = ''


# compile the list of 001s/003s and OCLC nums for the OCLC BATCH EXPORT records
try:
	orig_with_oclc_nums_txt = codecs.open(aco_globals.batch_folder+'/'+batch_name+'_1/'+batch_name+'_1_orig_with_oclc_nums.txt', 'r', encoding='utf8')	# opens the txt file containing the 001s, 003s, and corresponding OCLC nums (read-only)
	orig_with_oclc_nums_lines = orig_with_oclc_nums_txt.readlines()	# read the txt file containing 001/003 and corresponding OCLC numbers
	for line in orig_with_oclc_nums_lines:
		aco_globals.oclc_nums_bsns_all.append(line)
	orig_with_oclc_nums_txt.close()
except:
	orig_with_oclc_nums_lines = ''


# retrieve the CSV file containing the 003/001 values and corresponding URL handles
try:
	handles = open(aco_globals.batch_folder+'/handles.csv', 'r')
	aco_globals.handles_lines = handles.readlines()
	handles.close()
except:	handles = ''


# OUTPUT FILES
try:
	os.makedirs(upd_output_folder+'/'+batch_name+'_4_errors_no_880s/')
	os.makedirs(upd_output_folder+'/'+batch_name+'_4_errors_missing_key_880s/')
	os.makedirs(upd_output_folder+'/'+batch_name+'_4_errors_unlinked_880s/')
	os.makedirs(upd_output_folder+'/'+batch_name+'_4_errors_series/')
	os.makedirs(upd_output_folder+'/'+batch_name+'_4_errors_misc/')
except OSError as exception:
	if exception.errno != errno.EEXIST:
		raise

aco_globals.marcRecsOut_no_880s = pymarc.MARCWriter(file(upd_output_folder+'/'+batch_name+'_4_errors_no_880s/'+batch_name+'_4_no_880s.mrc', 'w'))
aco_globals.recs_no_880s_txt = codecs.open(upd_output_folder+'/'+batch_name+'_4_errors_no_880s/'+batch_name+'_4_no_880s.txt', 'w', encoding='utf8')
aco_globals.recs_no_880s_txt.write('Records with NO 880 script fields - batch '+batch_name+'\n')
aco_globals.recs_no_880s_txt.write('--  These records do NOT contain ANY 880 script fields\n')
aco_globals.recs_no_880s_txt.write('Report produced: '+aco_globals.curr_time+'\n')

aco_globals.marcRecsOut_missing_key_880s = pymarc.MARCWriter(file(upd_output_folder+'/'+batch_name+'_4_errors_missing_key_880s/'+batch_name+'_4_missing_key_880s.mrc', 'w'))
aco_globals.recs_missing_key_880s_txt = codecs.open(upd_output_folder+'/'+batch_name+'_4_errors_missing_key_880s/'+batch_name+'_4_missing_key_880s.txt', 'w', encoding='utf8')
aco_globals.recs_missing_key_880s_txt.write('Records MISSING KEY 880 script fields - batch '+batch_name+'\n')
aco_globals.recs_missing_key_880s_txt.write('--  At least one of the key fields is missing subfield $6,\n')
aco_globals.recs_missing_key_880s_txt.write('    so the corresponding 880 script field is missing or unlinked\n')
aco_globals.recs_missing_key_880s_txt.write('--  Key fields:\n    100, 110, 111, 130\n    240, 245, 246, 250, 260, 264\n    440, 490\n    700, 710, 711, 730\n    800, 810, 811, 830\n')
aco_globals.recs_missing_key_880s_txt.write('Report produced: '+aco_globals.curr_time+'\n')

aco_globals.marcRecsOut_unlinked_880s = pymarc.MARCWriter(file(upd_output_folder+'/'+batch_name+'_4_errors_unlinked_880s/'+batch_name+'_4_unlinked_880s.mrc', 'w'))
aco_globals.recs_unlinked_880s_txt = codecs.open(upd_output_folder+'/'+batch_name+'_4_errors_unlinked_880s/'+batch_name+'_4_unlinked_880s.txt', 'w', encoding='utf8')
aco_globals.recs_unlinked_880s_txt.write('Records containing UNLINKED 880 script fields - batch '+batch_name+'\n')
aco_globals.recs_unlinked_880s_txt.write('--  At least one 880 field has sequence number -00 in subfield $6,\n')
aco_globals.recs_unlinked_880s_txt.write('    meaning it is not linked to the corresponding parallel field\n')
aco_globals.recs_unlinked_880s_txt.write('Report produced: '+aco_globals.curr_time+'\n')

aco_globals.marcRecsOut_series_errors = pymarc.MARCWriter(file(upd_output_folder+'/'+batch_name+'_4_errors_series/'+batch_name+'_4_series_errors.mrc', 'w'))
aco_globals.recs_series_errors_txt = codecs.open(upd_output_folder+'/'+batch_name+'_4_errors_series/'+batch_name+'_4_series_errors.txt', 'w', encoding='utf8')
aco_globals.recs_series_errors_txt.write('Records containing SERIES errors - batch '+batch_name+'\n')
aco_globals.recs_series_errors_txt.write('--  These records contain an error with series headings in the 490/800/810/811/830 fields\n')
aco_globals.recs_series_errors_txt.write('--  Either the 490 field has 1st indicator=0 (untraced)\n')
aco_globals.recs_series_errors_txt.write('--  Or there are more 490 fields than there are 800/810/811/830 fields,\n')
aco_globals.recs_series_errors_txt.write('    so the corresponding 8XX heading needs added\n')
aco_globals.recs_series_errors_txt.write('Report produced: '+aco_globals.curr_time+'\n')

aco_globals.marcRecsOut_misc_errors = pymarc.MARCWriter(file(upd_output_folder+'/'+batch_name+'_4_errors_misc/'+batch_name+'_4_misc_errors.mrc', 'w'))
aco_globals.recs_misc_errors_txt = codecs.open(upd_output_folder+'/'+batch_name+'_4_errors_misc/'+batch_name+'_4_misc_errors.txt', 'w', encoding='utf8')
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
aco_globals.recs_misc_errors_txt.write('Report produced: '+aco_globals.curr_time+'\n')

aco_globals.marcRecsOut_errors_all = pymarc.MARCWriter(file(upd_output_folder+'/'+batch_name+'_4_errors_all.mrc', 'w'))
aco_globals.recs_errors_all_txt = codecs.open(upd_output_folder+'/'+batch_name+'_4_errors_all.txt', 'w', encoding='utf8')
aco_globals.recs_errors_all_txt.write('ALL Records containing any type of error - batch '+batch_name+'\n')
aco_globals.recs_errors_all_txt.write('--  Each of these records have one or more of the following errors:\n')
aco_globals.recs_errors_all_txt.write('    --  no 880 fields\n')
aco_globals.recs_errors_all_txt.write('    --  missing a key 880 field\n')
aco_globals.recs_errors_all_txt.write('    --  have an unlinked 880 field\n')
aco_globals.recs_errors_all_txt.write('    --  have a series heading error in the 490/800/810/811/830 fields\n')
aco_globals.recs_errors_all_txt.write('    --  have one of the various miscellaneous errors, marked with ERROR-MISC\n')
aco_globals.recs_errors_all_txt.write('Report produced: '+aco_globals.curr_time+'\n')

all_recs_analysis_txt = codecs.open(upd_output_folder+'/'+batch_name+'_4_all_recs_analysis.txt', 'w', encoding='utf8')

aco_globals.marcRecsOut_final_rnd = pymarc.MARCWriter(file(upd_output_folder+'/'+batch_name+'_5_final_recs.mrc', 'w'))
aco_globals.marcRecsOut_final_all = pymarc.MARCWriter(file(aco_globals.batch_folder+'/'+batch_name+'_5_final_recs.mrc', 'w'))
for final_rec in marcRecsIn_final_rnd:
	aco_globals.recs_final_rnd_count += 1
	aco_globals.marcRecsOut_final_rnd.write(final_rec)
	aco_globals.marcRecsOut_final_all.write(final_rec)
	rda_rec, msg = aco_functions.check_if_rda(final_rec)
	if rda_rec:
		aco_globals.recs_rda_count += 1

recs_final_rnd_count_input = aco_globals.recs_final_rnd_count

# MAIN PROCESSING AND STATISTICS ANALYSIS
rec_count_tot = 0				# variable to keep track of the total number of records processed in this batch
rec_count_file1 = 0				# variable to keep track of the number of records processed for File 1 (UPDATED records)

aco_globals.recs_no_880s_txt.write('---------------------------------------------------------------------\nFILE: '+updates_filename+'\n---------------------------------------------------------------------\n')
aco_globals.recs_missing_key_880s_txt.write('---------------------------------------------------------------------\nFILE: '+updates_filename+'\n---------------------------------------------------------------------\n')
aco_globals.recs_unlinked_880s_txt.write('---------------------------------------------------------------------\nFILE: '+updates_filename+'\n---------------------------------------------------------------------\n')
aco_globals.recs_series_errors_txt.write('---------------------------------------------------------------------\nFILE: '+updates_filename+'\n---------------------------------------------------------------------\n')
aco_globals.recs_misc_errors_txt.write('---------------------------------------------------------------------\nFILE: '+updates_filename+'\n---------------------------------------------------------------------\n')
aco_globals.recs_errors_all_txt.write('---------------------------------------------------------------------\nFILE: '+updates_filename+'\n---------------------------------------------------------------------\n')
for updated_rec in marcRecsIn_updates:
	dup_rec = aco_functions.process_rec(updated_rec, 'oclc')
	if not dup_rec:
		rec_count_file1 +=1

rec_count_tot = rec_count_file1 + recs_final_rnd_count_input

aco_globals.recs_no_880s_txt.write('TOTAL Number of Records with NO 880 script fields: '+str(aco_globals.recs_no_880s_count)+'\n\n')
aco_globals.recs_missing_key_880s_txt.write('TOTAL Number of Records missing key 880 script fields: '+str(aco_globals.recs_missing_key_880s_count)+'\n\n')
aco_globals.recs_unlinked_880s_txt.write('TOTAL Number of Records containing unlinked 880 script fields: '+str(aco_globals.recs_unlinked_880s_count)+'\n\n')
aco_globals.recs_series_errors_txt.write('TOTAL Number of Records containing series errors: '+str(aco_globals.recs_series_errors_count)+'\n\n')
aco_globals.recs_misc_errors_txt.write('TOTAL Number of Records containing miscellaneous errors: '+str(aco_globals.recs_misc_errors_count)+'\n\n')
aco_globals.recs_errors_all_txt.write('TOTAL Number of Records containing any type of error: '+str(aco_globals.recs_errors_all_count)+'\n\n')

aco_globals.all_recs_analysis_msg += 'Total UPDATED records processed - batch '+batch_name+': '+str(rec_count_tot)+' records\n'
aco_globals.all_recs_analysis_msg += 'Report produced: '+aco_globals.curr_time+'\n'
aco_globals.all_recs_analysis_msg += 'Input File 1 (updated recs): '+str(rec_count_file1)+'\n'
aco_globals.all_recs_analysis_msg += 'Input File 2 (final records prev round): '+str(recs_final_rnd_count_input)+'\n\n'

perc_errors_all = aco_functions.calculate_percentage(aco_globals.recs_errors_all_count,rec_count_tot)
perc_final_recs = aco_functions.calculate_percentage(aco_globals.recs_final_rnd_count,rec_count_tot)
perc_880s = aco_functions.calculate_percentage(aco_globals.recs_880s_count,rec_count_tot)
perc_no_880s = aco_functions.calculate_percentage(aco_globals.recs_no_880s_count,rec_count_tot)
perc_missing_key_880s = aco_functions.calculate_percentage(aco_globals.recs_missing_key_880s_count,rec_count_tot)
perc_unlinked_880s = aco_functions.calculate_percentage(aco_globals.recs_unlinked_880s_count,rec_count_tot)
perc_series_errors = aco_functions.calculate_percentage(aco_globals.recs_series_errors_count,rec_count_tot)
perc_misc_errors = aco_functions.calculate_percentage(aco_globals.recs_misc_errors_count,rec_count_tot)
perc_rda = aco_functions.calculate_percentage(aco_globals.recs_rda_count,rec_count_tot)

aco_globals.all_recs_analysis_msg += 'Records where OCLC nums did not match: '+str(aco_globals.recs_no_oclc_match_count)+'\n'
aco_globals.all_recs_analysis_msg += 'Total records containing any type of error for this round: '+str(aco_globals.recs_errors_all_count)+' ('+perc_errors_all+'%)\n'
aco_globals.all_recs_analysis_msg += 'Total records passing to final version for this round: '+str(aco_globals.recs_final_rnd_count)+' ('+perc_final_recs+'%)\n'
aco_globals.all_recs_analysis_msg += '-----------------------\n'
aco_globals.all_recs_analysis_msg += 'Records containing 880 script fields: '+str(aco_globals.recs_880s_count)+' ('+perc_880s+'%)\n'
aco_globals.all_recs_analysis_msg += 'Records with NO 880 script fields: '+str(aco_globals.recs_no_880s_count)+' ('+perc_no_880s+'%)\n'
aco_globals.all_recs_analysis_msg += 'Records missing key 880 script fields: '+str(aco_globals.recs_missing_key_880s_count)+' ('+perc_missing_key_880s+'%)\n'
aco_globals.all_recs_analysis_msg += 'Records containing unlinked 880 script fields: '+str(aco_globals.recs_unlinked_880s_count)+' ('+perc_unlinked_880s+'%)\n'
aco_globals.all_recs_analysis_msg += 'Records containing series errors in 490/800/810/811/830 fields: '+str(aco_globals.recs_series_errors_count)+' ('+perc_series_errors+'%)\n'
aco_globals.all_recs_analysis_msg += 'Records containing miscellaneous errors: '+str(aco_globals.recs_misc_errors_count)+' ('+perc_misc_errors+'%)\n'
aco_globals.all_recs_analysis_msg += 'Records containing bad encoding replacement character: '+str(aco_globals.recs_repl_char_count)+'\n'
aco_globals.all_recs_analysis_msg += 'Records containing RDA fields: '+str(aco_globals.recs_rda_count)+' ('+perc_rda+'%)\n'
aco_globals.all_recs_analysis_msg += '---------------------------------------------------------------------\nINDIVIDUAL RECORDS ANALYSIS:\n---------------------------------------------------------------------\n'

all_recs_analysis_txt.write(aco_globals.all_recs_analysis_msg)
all_recs_analysis_txt.write(aco_globals.indiv_rec_analysis_msgs)
print str(rec_count_tot)+' records were processed in all UPDATED files'

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
aco_globals.marcRecsOut_final_rnd.close()
aco_globals.marcRecsOut_final_all.close()
