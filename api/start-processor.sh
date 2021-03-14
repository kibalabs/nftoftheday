#!/usr/bin/env bash
set -e -o pipefail

python process_blocks.py -s $1 -e $2 -b $3
