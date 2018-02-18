#!/usr/bin/env bash

echo "Start AutoPEP8 ! "
FILES=$(git diff --name-only | grep -e '\.py$')
for one_file in $FILES
do
    # auto pep8 correction
    autopep8 --in-place --aggressive --max-line-length 600 $one_file
done
echo "End AutoPEP8 ! "
