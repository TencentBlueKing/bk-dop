#!/bin/bash

set -x

echo "git log: $BK_CI_REPO_GIT_WEBHOOK_COMMITID"
DIFF_FILES=$(git log -m -1 --name-only --pretty="format:" $BK_CI_REPO_GIT_WEBHOOK_COMMITID)

echo -e "[merge_ci]: git diff files \n#############\n $DIFF_FILES \n#############\n"

