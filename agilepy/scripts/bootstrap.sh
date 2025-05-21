#!/bin/bash

set -u
set -v
set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

Help()
{
   # Display Help
   echo "This script Execute will change the user inside the container to your local user to avoid permission issues."
   echo
   printf "\n\33[32mSyntax: bootstrap.sh [-h | -o] [tag]\33[0m\n"
   echo 
   echo "Options:"
   echo "  h     Print this Help."
   echo "  o     Overwrite image. If provided, the original image will be overwritten. If not provided, the username will be appended to the tag and the original image will be kept."
   echo 
   echo "Arguments:"
   echo "  tag   The tag of the image to be boostrapped."
   echo
}

export DUPLICATE_IMAGE=true

while getopts ":h:d" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      o) # overwrite image
         export DUPLICATE_IMAGE=false
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


: '
   $1:$2 is the repository:tag of the image to be boostrapped.
   $3 is DUPLICATE_IMAGE. If false, the original image will be overwritten.
'
boostrap() {
   MY_UID="$(id -u)"
   MY_GID="$(id -g)"
   AGILEPY_TAG="agilescience/$1:$2"
   INTERMEDIATE_TAG=local/delete_me_soon:latest

   # just make sure the SDE exists on this machine
   if [[ "$(docker images -q $AGILEPY_TAG 2> /dev/null)" == "" ]]; then
      printf "\n\33[31mImage $AGILEPY_TAG does not exist locally, pull it from DockerHub.\n\33[0m\n"
      return;
   fi
   
   docker tag $AGILEPY_TAG $INTERMEDIATE_TAG

   # check if $3 is false
   if [[ $3 == false ]]; then
      docker rmi $AGILEPY_TAG
      printf "\n\33[31mThe original image will be deleted.\33[0m\n"
   else
      AGILEPY_TAG=$AGILEPY_TAG\_$(whoami)
      printf "\n\33[32mThe original image will be kept. The new image will have the following tag: '$AGILEPY_TAG'\33[0m\n"        
   fi
   
   printf "\n\33[32mBuilding image $AGILEPY_TAG\33[0m\n"
   
docker build \
--tag $AGILEPY_TAG \
- <<EOF
FROM ${INTERMEDIATE_TAG} 
USER root
RUN usermod -u ${MY_UID} flareadvocate && \
   groupadd -o --gid ${MY_GID} hostg && \
   usermod -a -G hostg flareadvocate && \
   usermod -g ${MY_GID} flareadvocate
USER flareadvocate
EOF
docker rmi $INTERMEDIATE_TAG

printf "\33[32mDone!\33[0m\n"

}


# TAG is the last argument
TAG=${@: -1}

boostrap agilepy $TAG $DUPLICATE_IMAGE 


