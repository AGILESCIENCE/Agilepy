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
docker rmi $AGILEPY_TAG
docker build \
--tag $AGILEPY_TAG \
- <<EOF
FROM ${INTERMEDIATE_TAG}
USER root
RUN usermod -u "${MY_UID}" flareadvocate && groupmod -g "${MY_GID}" flareadvocate
USER flareadvocate
EOF
docker rmi $INTERMEDIATE_TAG

printf "\33[32mDone!\33[0m\n"

}