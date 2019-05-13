#!/bin/bash

for f in *.txt
do
    echo $f
    if grep -q "o zmianie ustawy\|o zmianie niektórych ustaw" $f; then
        mv $f first/$f
    else
        mv $f second/$f
    fi
done

