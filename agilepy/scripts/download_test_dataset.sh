#!/bin/bash
set -e

# Set the directory path (change this to your target directory)
DIR="$AGILE/agilepy-test-data/"

# # Check if the directory exists
# if [ -d "$DIR" ]; then
#   echo "Directory $DIR exists. Removing it..."
#   rm -rf "$DIR"
#   echo "Directory removed."
# else
#   echo "Directory $DIR does not exist."
# fi
# 
# # Create the directory
# mkdir -p "$DIR"
# echo "Directory $DIR created."

# Move into the directory
cd "$DIR" || { echo "Failed to enter directory $DIR"; exit 1; }
echo "Now inside $DIR"

# Download test dataset
echo "Download test dataset..."

# These are downloaded in the base image
# wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1B31SCrHoOU0KnZoaZ7NTq6nY_PTD-ner' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1B31SCrHoOU0KnZoaZ7NTq6nY_PTD-ner" -O test_dataset_6.0.tar.gz && rm -rf /tmp/cookies.txt && \
# tar -xzf test_dataset_6.0.tar.gz && \
# rm test_dataset_6.0.tar.gz

# wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1B3Tp-01-X7Cwh6lq11BUCiaHuctj0iDW' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1B3Tp-01-X7Cwh6lq11BUCiaHuctj0iDW" -O test_dataset_agn.tar.gz && rm -rf /tmp/cookies.txt && \
# tar -xzf test_dataset_agn.tar.gz && \
# rm test_dataset_agn.tar.gz

wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1dRfBltxWvijKjxgU9lHTJRm--l8tbgGZ' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1dRfBltxWvijKjxgU9lHTJRm--l8tbgGZ" -O bayesian_blocks.tar.gz && rm -rf /tmp/cookies.txt && \
tar -xzf bayesian_blocks.tar.gz && \
rm bayesian_blocks.tar.gz

# End
echo "Download completed!"
