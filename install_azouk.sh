#!/bin/bash
cd azouk-libraries/src/azouk
echo "Applying patch..."
patch -p0 -i ../../../azouk_r43_patch.txt
echo "Replacing multiplexer.rules"
rm multiplexer.rules
ln -s ../../../multiplexer.rules .
cd ..
make


