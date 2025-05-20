#!/bin/bash
# (C) 2025 GoodData Corporation
#
# (C) 2023 GoodData Corporation
#

DIR=$(echo $(cd $(dirname "${BASH_SOURCE[0]}") && pwd -P))

docker build -t pysdk/buf -f "${DIR}/Dockerfile" "$DIR"

#
# Note the HOME funny stuff. The `buf` tool needs to create a .cache directory. It tries
# to do that under HOME and if HOME is not set then under root dir. Now, since the container does not
# run as root, it will not be able to create that directory. Setting HOME env var to a writable directory
# works this around.
#

echo "+---------------------------------------------------------------------+"
echo "| Running dockerized buf (https://github.com/bufbuild/buf)            |"
echo "+---------------------------------------------------------------------+"

if [[ $(realpath "$(command -v docker)") =~ .*podman.* ]]; then # if podman is installed, do not override user, since podman runs rootless
  override_user=
else # docker runs under root, thus we want to change the user to current one not to generate files under the root user
  override_user="--user $(id -u):$(id -g)"
fi

docker run \
  ${override_user} \
  --volume "${DIR}:/workspace" \
  --workdir /workspace \
  --env HOME=/tmp \
  --rm \
  pysdk/buf \
  generate $*
