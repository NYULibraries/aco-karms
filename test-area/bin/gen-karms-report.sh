#!/bin/bash
VERSION='0.1.0'
BSN_SE_MAP_FILENAME='bsn-se-map.csv'
#------------------------------------------------------------------------------
# Time-stamp: <2016-10-05 10:07:18 jgp>
#------------------------------------------------------------------------------
#
# Usage: $0 
#
# Assumptions:
# Script assumes that final component of /path/to/wip is the digitization id
#
# Flow:
# assert argument count
# expand path
# extract digitization id
# check if published
# pushd into wip/aux directory
# rm -f *
# check exit status
# popd
# exit pass with rm -f exit status
#------------------------------------------------------------------------------
# institution,original_bsn,se_num,se_vol,pub_batch,oclc,digital_bsn,notes
# ./work/NjP/NjP_20160504/bsn-se-map.csv
# b12377740,aub_aco000005:v.1|aub_aco000006:v.2|aub_aco000007:v.3|aub_aco000008:v.4|aub_aco000009:v.5|aub_aco000010:v.6|aub_aco000011:v.7|aub_aco000012:v.8

set -u

READLINK='/usr/bin/readlink'
BASENAME='/bin/basename'

#------------------------------------------------------------------------------
ok_exit() {
    exit 0
}

err_exit() {
    exit 1
}

print_usage() {
    echo "$0"
}

not_implemented() {
    print_warning_msg "function not implemented : ${FUNCNAME[1]}"
}

print_error_exit() {
    print_error_msg "$1"
    err_exit
}

print_error_msg() {
    echo "ERROR: $1" >&2
}

print_warning_msg() {
    echo "WARNING: $1" >&2
}

assert_argument_count() {
    expected="$1"
    actual="$2"

    if [[ "$expected" != "$actual" ]]; then
	print_error_msg "incorrect argument count"
	print_usage
	err_exit
    fi
}

print_header() {
    echo 'institution,original_bsn,se_map,pub_batch,oclc,digital_bsn,notes'
}

print_footer() {
    echo "success"
}

assert_in_project_root_dir() {
    # this script must be run from the aco-karms project root directory
    assert_dir_exists './work' 'could not find work/ directory. please run from aco-karms project root'
}

assert_dir_exists() {
    if [[ ! -d "$1" ]]; then
	print_error_exit "$2"
    fi
}

process_file() {
    local line
    local original_bsn
    local se_map
    local oclc=''          # not implemented
    local digital_bsn=''   # not implemented
    local notes=''         # not implemented
    while read line ; do
	original_bsn=$(echo $line | cut -d',' -f1)
	se_map=$(echo $line | cut -d',' -f2-)
	echo "${institution},${original_bsn},${se_map},${pub_batch},${oclc},${digital_bsn},${notes}"
    done < $1
}

# institution,original_bsn,se_map,pub_batch,oclc,digital_bsn,notes
# ./work/NjP/NjP_20160504/bsn-se-map.csv
# b12377740,aub_aco000005:v.1|aub_aco000006:v.2|aub_aco000007:v.3|aub_aco000008:v.4|aub_aco000009:v.5|aub_aco000010:v.6|aub_aco000011:v.7|aub_aco000012:v.8
crawl_and_print() {
    FILES=$(find . -type f -name "${BSN_SE_MAP_FILENAME}" | sort)
    local f
    for f in $FILES; do
	institution=$(echo "$f" | cut -d'/' -f3)
	pub_batch=$(echo "$f" | cut -d'/' -f4)
	process_file "$f"
    done
}     
    
#------------------------------------------------------------------------------
# MAIN ROUTINE
#------------------------------------------------------------------------------
main() {
    assert_argument_count 0 "$#"
    assert_in_project_root_dir
    print_header
    crawl_and_print
    ok_exit
}

main "$@"

