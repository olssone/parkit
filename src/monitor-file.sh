#!/bin/bash

DATAFILE=".datafile"

FILE_TO_MONITOR="$(cat $DATAFILE)"
echo $FILE_TO_MONITOR
# Check if the file exists
if [ ! -f "$FILE_TO_MONITOR" ]; then
    echo "File not found: $FILE_TO_MONITOR"
    exit 1
fi

# Initial read of the last line
LAST_LINE=$(tail -n 1 "$FILE_TO_MONITOR")

# Monitor the file
while true; do
    NEW_LAST_LINE=$(tail -n 1 "$FILE_TO_MONITOR")

    if [ "$LAST_LINE" != "$NEW_LAST_LINE" ]; then
        echo "$NEW_LAST_LINE"
        ssh -q pluto.hood.edu "echo '$NEW_LAST_LINE' >> ~/public_html/datarecord.txt" 2>/dev/null
        LAST_LINE="$NEW_LAST_LINE"
    fi

    sleep 1  # Check every 1 second
done