.. obci_control documentation master file, created by
   sphinx-quickstart on Thu Nov 10 11:21:47 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to obci_control's documentation!
========================================

Here are/will be documented the following features of `OpenBCI`_ system control tools:

.. _OpenBCI: http://bci.fuw.edu.pl/wiki/Main_Page

* Configuration of OpenBCI modules
* Passing configuration parameters between OpenBCI modules
* Making launch files with experiment scenarios
* Using launcher
* Launcher and configuration modules' source code

Glossary
--------

Useful terms for easy understanding of the documentation:

**peer**
	An OpenBCI module (most probably a Python program) which communicates with other running modules through the network (using Multiplexer for message passing). Typical examples: eeg signal amplifiers, filters, signal displays.

(helper) **module**
	A module which is not a peer. Helper modules are not explicitly mentioned in OpenBCI launch/configuration files because they are components of the peers.

**peer config file**, configuration file
	Text configuration file (of a peer). Stores necessary parameters and defines dependencies on other peers in the system.

**experiment**, OpenBCI instance, system instance
	A set of running OBCI peers. Each peer can be identified by its assigned peer_id, thus allowing for launching multiple instances of the same programs. Peer_ids, peer program paths and peer configurations are predefined in *launch files*.

**launch file**, experiment definition file/scenario, *scenariusz eksperymentu*
	Text file for defining an experiment. It contains paths to programs to be executed (peers),
	assignments of peer_id and paths to peer configurations.

Peer configuration tutorial
---------------------------

:doc:`peer configuration tutorial<configuration/tutorial>`



Contents:
---------

.. toctree::
   :maxdepth: 2

   configuration/tutorial

   apidoc/modules
   apidoc/common
   apidoc/peer
   apidoc/launcher




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`