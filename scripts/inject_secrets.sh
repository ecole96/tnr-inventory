#!/bin/sh

# utility for injecting Docker secrets into ENV variables
# in the compose file, we define secret-based ENVs with the intended variable name, but append _FILE to the end and set the value to the secret file path
# this script gathers these variables, creates new ENVs with _FILE sliced off the name and sets them to the secret value
# for example, "MY_VARIABLE_FILE=/run/secrets/my_variable" in the compose file will result in MY_VARIABLE being set with the file contents of /run/secrets/my_variable
# this is mainly intended for the entrypoint, but if you exec into the container the variables generated there will not be in your shell
# so, run this script manually when working in the shell: ". /scripts/inject_secrets.sh"

set -eu

# inject Docker secrets as ENV variables
PATTERN=_FILE

# get all ENVs ending in _FILE
FILE_ENVS="$(printenv | grep "$PATTERN=" | cut -f1 -d"=")"

for FILE_ENV in "$FILE_ENVS" # loop through each found ENV
do
    eval SECRET_FILE="\$$FILE_ENV"
    ENV_NAME="$(echo $FILE_ENV | sed -e "s/$PATTERN//")" 
    echo "ENV [$FILE_ENV -> $ENV_NAME] Secret file: $SECRET_FILE"
    if [ -f "$SECRET_FILE" ]; then
        ENV_VALUE="$(cat "$SECRET_FILE")"
        export "$ENV_NAME"="$ENV_VALUE" # set variable in container
    else
        echo "Secret file does not exist! $SECRET_FILE"
    fi
done