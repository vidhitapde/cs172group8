#! /bin/bash

YELLOW='\033[0;33m' 
RED='\033[0;31m'
NC='\033[0m' # No Color reset

if [ "$#" -lt 4 ]; then
    echo -e "${YELLOW}Usage: $0 <seed-file> <max-pages> <max-depth> <output-dir> [time-limit_secs]${NC}"
    exit 1
fi

SEED_FILE=$1
MAX_PAGES=$2
MAX_DEPTH=$3
OUTPUT_FILE=$4
TIME_LIMIT=${5:-3600} #Default to 60 minutes

if [ ! -f "$SEED_FILE" ]; then
    echo -e "${RED}Err: Specified Seed file not found!${NC}"
    exit 1
fi

python3 scrape.py "$SEED_FILE" "$MAX_PAGES" "$MAX_DEPTH" "$OUTPUT_FILE" "$TIME_LIMIT"
