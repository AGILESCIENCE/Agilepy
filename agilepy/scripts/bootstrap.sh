#!/bin/bash

set -u
set -v
set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source $SCRIPT_DIR/utilities.sh > /dev/null

Help()
{
   # Display Help
   echo "This script Execute will change the user inside the container to your local user to avoid permission issues."
   echo
   printf "\n\33[32mSyntax: bootstrap.sh [-h | -d] [tag]\33[0m\n"
   echo 
   echo "Options:"
   echo "  h     Print this Help."
   echo "  d     Duplicate image. If not provided, the original image will be overwritten. If provided, the username will be appended to the tag and the original image will be kept."
   echo 
   echo "Arguments:"
   echo "  tag   The tag of the image to be boostrapped."
   echo
}

export DUPLICATE_IMAGE=false

while getopts ":h:d" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      d) # duplicate image
         export DUPLICATE_IMAGE=true
         ;;
     \?) # incorrect option
         echo "Error: Invalid option"
         exit;;
   esac
done

# if no arguments supplied, display usage
if [  $# -le 0 ]; then
   Help
   exit 1
fi

# TAG is the last argument
TAG=${@: -1}

boostrap agilepy $TAG $DUPLICATE_IMAGE 


