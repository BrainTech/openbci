1. Assumed You have MX downloaded
2. Apply patch for given sampling frequency eg: (in MX dir) patch -p0 -i mx_37_2048.txt
3. make

4. If you want to change patch do:
5. svn revert azouk/multiplexer/io/* && rm azouk/multiplexer/io/Logger.h
6. and apply patch one again
