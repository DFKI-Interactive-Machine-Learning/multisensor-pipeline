# Installation

This document provides an installation guide for users of Multisensor pipeline.

## Operating System

Multisensor Pipeline supports Linux, macOS and Windows.
Other operating systems might also work,
  but we do not make any claims about them.

## Package Manager

Multisensor Pipeline depends on some libraries being available.
So we need to make sure they are installed.
To ease their installation process, we recommend using a package manager.

On Linux:

-   There is usually a package manager provided by your distributor.
    Please refer to the distribution documentation on how to initialize it.

On macOS:

-   There are multiple package managers available,
    but we recommend [using Homebrew](https://brew.sh/index_de):
    -     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    -     echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> /Users/bengt/.zprofile  
    -     eval "$(/opt/homebrew/bin/brew shellenv)"
    -   Restart the shell you executed this in.

On Windows:

-   TODO You can probably just use Anaconda. Still, provide details here.

## Python Package Manager

If you intend to use Multisensor Pipeline
  as an abstraction layer from its dependencies,
  you probably want the easiest possible way of installing it.
In this case,
  you should be able to get away with using an Anaconda environment.
To install Anaconda, follow the instructions on their website:

<https://docs.anaconda.com/anaconda/install/index.html>

> Note:
>     On macOS, this is supported on x86 CPUs, only.
>     On machines with Apple Silicon using the ARM architecture,
>     please refer to the following developer installation:

If you are a developer of Multisensor Pipeline,
  you might want to report bugs to the dependency packages.
For a smooth issue submission process,
  you probably want to install the official packages,
  provided by the library authors,
  from the Python Package Index (PyPI).
In this case,
  you can use the tools provided by your python installation.
To bootstrap the Python package manager pip from the standard library,
  run:

    python3 -m ensure pip

## Libraries

Some of our dependencies require libraries at compile time.
So, we install them beforehand:

On Linux:

TODO

On macOS (Intel / x86):

    brew install \
        jpeg \
        openblas \
        cmake \
        portaudio \
        pkgconfig

On macOS (Apple / ARM64):

    brew install \
        jpeg \
        openblas \
        cmake \
        pkgconfig

On Windows:

    conda install portaudio

## Python

Multisensor pipeline should work with any supported version of the Python interpreter.
To install or upgrade your Python interpreter, please refer to their documentation:

<https://wiki.python.org/moin/BeginnersGuide/Download>

## Virtual Environment

Installing Python libraries system-wide can lead to unforeseen consequences.
In order to avoid this class of errors,
    Multisensor Pipeline should be installed into a virtual environment.
To create a local environment, run:

On Linux:

    conda create \
        --channel conda-forge \
        -p .condaenv \
        --file requirements.d/pytest-macos.txt

On macOS (Intel / x86_64):

    conda create \
        --channel conda-forge \
        -p .condaenv \
        --file requirements.d/pytest-macos.txt

On macOS (Apple / ARM):

-   Open a terminal in your working copy of multisensor pipeline
-   Create an empty virtual environment:  
    `python -m venv venv`
-   Install most of the requirements:  
    `venv/bin/python3 -m pip install
        -r requirements.d/pytest-macos-m1-pip-source.txt`
-   Change to the directory containing the MSP repository:  
    `cd ..`
-   Download PyAudio:  
    `git clone
        https://people.csail.mit.edu/hubert/git/pyaudio.git`  
    `cd pyaudio`
-   Download and build portaudio from source:  
    `git clone
        --depth 1
        --branch v19.7.0
        https://github.com/PortAudio/portaudio.git
        portaudio-v19`  
    `cd portaudio-v19`  
    `./configure`  
    `make`  
    `cd ../`
-   Build pyaudio, linking it against portaudio:  
    `export
        CFLAGS="-I `pwd`/portaudio-v19/include/ -L `pwd`/portaudio-v19/lib/.libs/"`  
    `python setup.py build --static-link`
-   Install PyAudio into the virtual environment:  
    `../multisensor-pipeline/venv/bin/python3 
    setup.py install`
-   Download OpenCV:  
    `cd ..`  
    `git clone --depth 1 --recursive https://github.com/opencv/opencv-python.git`  
    `cd opencv`
-   Install OpenCV's installation requirements:  
    `../multisensor-pipeline/venv/bin/python3
        -m pip install scikit-build`
-   Install OpenCV into the virtual environment:  
    `../multisensor-pipeline/venv/bin/python3
        setup.py install`  
    `cd ../multisensor-pipeline`

On Windows:

    conda create \
        --channel conda-forge \
        -p .condaenv \
        --file requirements.d\pytest-windows.txt

## Testing

On Linux:

    ./.condaenv/bin/python -m pytest multisensor_pipeline

On macOS (Intel / x86):

    ./.condaenv/bin/python -m pytest multisensor_pipeline

On macOS (Apple / ARM):

    ./venv/bin/python -m pytest multisensor_pipeline

On Windows:

    .\.condaenv\bin\python -m pytest multisensor_pipeline

## Installation

To actually install the `multisensor_pipeline` into the environment,
  run one of the following commands:

*   To install from PyPi, run:  
    `.condaenv/bin/python -m pip install multisensor-pipeline`

*   To install a pre-built wheel, run:  
    `.condaenv/bin/python -m pip install multisensor_pipeline-<version>-<meta-info>.whl`

*   To install from source, run (in a working copy of the repository):  
    `.condaenv/bin/python setup.py install`
