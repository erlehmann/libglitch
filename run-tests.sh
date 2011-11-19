#!/bin/sh

for f in `ls -1 tests/*.glitch`; do
    echo $f
    ./glitter.py `cat $f` | head -c512;
done
