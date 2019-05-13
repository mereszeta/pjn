#!/bin/bash

for f in *.txt
do
    sed -i '' '/^ *$/d' $f
    sed -i '' 's/ \{1,\}/ /g' $f
done
