#!/bin/bash

# This script pulls from the cornell metadata harvest site as part of the ACO project
wget -e robots=off -r --no-parent --reject 'index.html*' http://oai.library.cornell.edu/nyu/
