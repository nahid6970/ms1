#!/bin/bash

if [ $# -lt 4 ]; then
    echo "Usage: $0 <input_file> <output_file> <dimension> <max_size_kb>"
    echo "Example: $0 input.pdf output.jpg 800x800 400"
    echo "Example: $0 input.jpg output.pdf 1200x1200 500"
    exit 1
fi

INPUT="$1"
OUTPUT="$2"
DIM="$3"
MAX_KB="$4"

EXT="${OUTPUT##*.}"
QUALITY=95

# PDF to Image
if [[ "$INPUT" == *.pdf ]]; then
    convert -density 150 "$INPUT[0]" -resize "$DIM" -quality $QUALITY -background white -alpha remove "$OUTPUT"
# Image to PDF
elif [[ "$OUTPUT" == *.pdf ]]; then
    convert "$INPUT" -resize "$DIM" -quality $QUALITY "$OUTPUT"
# Image to Image
else
    convert "$INPUT" -resize "$DIM" -quality $QUALITY "$OUTPUT"
fi

# Reduce quality if file is too large
while [ $(stat -f%z "$OUTPUT" 2>/dev/null || stat -c%s "$OUTPUT") -gt $((MAX_KB * 1024)) ] && [ $QUALITY -gt 50 ]; do
    QUALITY=$((QUALITY - 5))
    if [[ "$INPUT" == *.pdf ]]; then
        convert -density 150 "$INPUT[0]" -resize "$DIM" -quality $QUALITY -background white -alpha remove "$OUTPUT"
    elif [[ "$OUTPUT" == *.pdf ]]; then
        convert "$INPUT" -resize "$DIM" -quality $QUALITY "$OUTPUT"
    else
        convert "$INPUT" -resize "$DIM" -quality $QUALITY "$OUTPUT"
    fi
done

SIZE=$(stat -f%z "$OUTPUT" 2>/dev/null || stat -c%s "$OUTPUT")
echo "Created: $OUTPUT (${DIM}, $((SIZE / 1024))KB)"
