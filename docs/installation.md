# Installation

This document provides an installation guide for users of Multisensor pipeline.

## Operating System

Multisensor Pipeline supports Linux, macOS and Windows.
Other operating systems might also work,
  but we do not make any claims about them.

## Python

Multisensor pipeline should work with Python interpreter starting from 3.6 (x64).
To install or upgrade your Python interpreter, please refer to their documentation:

<https://wiki.python.org/moin/BeginnersGuide/Download>

To make sure that a Python interpreter is available, run: 

    python --version


## Installation

To install the `multisensor_pipeline`,
  run one of the following commands:

To install from PyPi, run:  

    python -m pip install multisensor-pipeline

To install a pre-built wheel, run:  

    python -m pip install multisensor_pipeline-<version>-<meta-info>.whl

To install from source, run (in a working copy of the repository):  

    python setup.py install
