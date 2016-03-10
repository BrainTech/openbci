In order to be able to generate documentation, on Ubuntu first you must install Sphinx, for example from apt-get with the following bash command:

sudo apt-get install python-sphinx

Next, to build the documentation, from the openbci/docs/ directory run:

make html

HTML documentation will be created in the directory openbci/docs/_build/html, with the file index.html being an entry point. Before any re-building of documentation, first run:

make clean

to clean everything that has been builded previously.


