#!/bin/bash

# This script pulls from the columbia metadata harvest site as part of the ACO project
wget -e robots=off -r --no-parent --reject 'index.html*' https://ulib.aub.edu.lb/aco/
