#!/bin/bash

set -e

CURRENT_PATH=$(cd $(dirname $BASH_SOURCE); pwd)
OPERATOR=$1
COMMIT_FILE=$2

if [ "$OPERATOR" == "update" ]
then
    git add $COMMIT_FILE
elif [ "$OPERATOR" == "delete" ]
then
    git rm $COMMIT_FILE
fi

git commit -m "update $COMMIT_FILE"
git push origin master


