#!/bin/bash

YELLOW='\033[0;33m' 
RED='\033[0;31m'
NC='\033[0m' # No Color reset

if [ "$#" -ne 1 ]; then
    echo -e "${YELLOW}Usage: $0 <html_input_folder>${NC}"
    exit 1
fi

INPUT_DIRECTORY=$1


if [ ! -d "$INPUT_DIRECTORY" ]; then
    echo -e "${RED}Err: Input Directory not found!${NC}"
    exit 1
fi

python3 index.py "$INPUT_DIRECTORY"
python3 hello.py