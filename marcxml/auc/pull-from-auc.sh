#!/bin/bash

# This script pulls from the metadata harvest site as part of the ACO project
wget -e robots=off -r --no-parent --reject 'index.html*' http://libm.aucegypt.edu/aco/
