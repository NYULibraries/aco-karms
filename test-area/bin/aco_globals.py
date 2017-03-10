import datetime
import os

curr_time = str(datetime.datetime.today())

parent_dir = os.path.dirname(os.getcwd())
work_folder = parent_dir+'/work'
batch_folder = work_folder
handles_lines = ''			# variable to contain the lines from the CSV file containing the 003/001 values and corresponding URL handle
bsn_se_lines = ''			# variable to contain the lines from the CSV file containing the BSNs and SE (source entity) values

indiv_rec_analysis_msgs = ''	# variable to compile all individual analysis messages for all records
all_recs_analysis_msg = ''		# variable to collect record analysis messages, statistics, etc.

oclc_nums_bsns_all = []			# variable to compile the lines of original BSNs (001s/003s) and their corresponding OCLC numbers, for all records in the batch having an OCLC record
oclc_nums_processed = set()		# variable to keep track of all oclc numbers processed

recs_no_oclc_match_count = 0		# number of OCLC record numbers that did not match an original record
recs_errors_all_count = 0			# total records having either a 490/800/810/811/830 series or 880 script error
recs_final_prev_subset_count = 0	# total records passing errors criteria and saving to "final" version for previous round of analysis
recs_final_this_subset_count = 0	# total records passing errors criteria and saving to "final" version for just this round of updates (excludes count of previous final subset)
recs_final_curr_subset_count = 0	# total records passing errors criteria and saving to "final" version for current round of analysis (includes count of previous final subset)
recs_880s_count = 0					# total records having 880 script fields
recs_no_880s_count = 0				# total records NOT having any 880 script fields
recs_missing_key_880s_count = 0		# total records missing a key 880 script field
recs_unlinked_880s_count = 0		# total records having an unlinked 880 field
recs_series_errors_count = 0		# total records having series errors for 490 + 800/810/830 fields
recs_misc_errors_count = 0			# total records having miscellaneous errors (unrelated to 880 fields)
recs_repl_char_count = 0			# total records containing the bad encoding replacement character
recs_rda_count = 0					# total records having RDA 3XX or 040e fields
recs_no_call_num_count = 0			# total records missing an LC call number - no 050 or 090 field


# OUTPUT FILES from aco_process scripts
marcRecsOut_no_880s = ''
recs_no_880s_txt = ''

marcRecsOut_missing_key_880s = ''
recs_missing_key_880s_txt = ''

marcRecsOut_unlinked_880s = ''
recs_unlinked_880s_txt = ''

marcRecsOut_series_errors = ''
recs_series_errors_txt = ''

marcRecsOut_misc_errors = ''
recs_misc_errors_txt = ''

marcRecsOut_errors_all = ''
recs_errors_all_txt = ''

marcRecsOut_final_subset = ''
marcRecsOut_final_all = ''
