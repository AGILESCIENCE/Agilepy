#!/bin/bash
set -euo pipefail

# Set the directory path (change this to your target directory)
DIR="$AGILE/agilepy-test-data/"

# Ensure directory exists
mkdir -p "$DIR"

# Move into the directory
cd "$DIR" || { echo "Failed to enter directory $DIR"; exit 1; }
echo "Now inside $DIR"

# Download test dataset
echo "Download test dataset..."

# Function to download and extract only if missing
download_and_extract() {
    local id="$1"
    local tar_name="$2"
    local extract_dir="$3"

    if [ -d "$extract_dir" ]; then
        echo " $extract_dir already exists, skipping download."
    else
        echo " Downloading $tar_name ..."
        wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate "https://docs.google.com/uc?export=download&id=$id" -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1/p')&id=$id" -O "$tar_name" && \
        rm -f /tmp/cookies.txt && \
        tar -xzf "$tar_name" && \
        rm "$tar_name"

        echo " Extracted $extract_dir"
    fi
}

# Datasets
download_and_extract "1B31SCrHoOU0KnZoaZ7NTq6nY_PTD-ner" "test_dataset_6.0.tar.gz" "test_dataset_6.0"
download_and_extract "1B3Tp-01-X7Cwh6lq11BUCiaHuctj0iDW" "test_dataset_agn.tar.gz" "test_dataset_agn"
download_and_extract "1dRfBltxWvijKjxgU9lHTJRm--l8tbgGZ" "bayesian_blocks.tar.gz" "bayesian_blocks"
download_and_extract "1m7DhHHxiU3Q81biNvTGRAhFjP0j5IJfL" "ratemeters.tar.gz" "ratemeters"

# End
echo "Download completed!"
