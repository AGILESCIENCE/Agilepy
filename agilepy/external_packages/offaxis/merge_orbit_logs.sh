#!/bin/bash
file1=$1
output=$2

if [ -e ${output} ]; then
    rm ${output}
fi

echo "Merging information from AGILE LOG files..."
echo "This might take a while..."
ftmerge @${file1} $output lastkey='TSTOP, DATE-END' columns="TIME,INSTR_STATUS,ATTITUDE_RA_Y,ATTITUDE_DEC_Y,MODE,PHASE,LIVETIME,LOG_STATUS"

echo "Done!"
