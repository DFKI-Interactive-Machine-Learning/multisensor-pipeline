# Installation

## Operating System

Multisensor Pipeline supports Linux, macOS and Windows.
Others might also work, but we do not make any claims about them.
For installing libraries on macOS, we need homebrew's brew command:

## Package Manager

Multisensor Pipeline depends on some libraries being available.
So we need to make sure they are installed.
To ease their installation process, we recommend using a package manager.

On Linux:

-   There usually is a package manager provided by your distributor.
    Please refer to the distribution documentation on how to initialize.

On macOS:

-     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
-     echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> /Users/bengt/.zprofile  
-     eval "$(/opt/homebrew/bin/brew shellenv)"
-   Restart the shell you executed this in.

Source: <https://brew.sh/index_de>

On Windows:

-   You can probably just use Anaconda.

## Anaconda

On client machines, we recommend using an Anaconda environment.
To follow our recommendation, install Anaconda from their website:

<https://docs.anaconda.com/anaconda/install/index.html>

## Libraries

Some of our dependencies require libraries at compile time.
So, we install them beforehand:

On Linux:

TODO

On macOS:

    brew install \
        jpeg \
        openblas \
        cmake \
        portaudio \
        pkgconfig

On Windows:

    conda install portaudio

## Python

Multisensor pipeline should work with any supported version of the Python interpreter.
To install or upgrade your Python interpreter, please refer to their documentation:

<https://wiki.python.org/moin/BeginnersGuide/Download>

## Environment

Multisensor Pipeline should be installed into a virtual environment.
To create a local environment using Conda, run:

On Linux:

    conda create \
        --channel conda-forge \
        -p .condaenv \
        --file requirements.d/pytest-macos.txt

On macOS:

    conda create \
        --channel conda-forge \
        -p .condaenv \
        --file requirements.d/pytest-macos.txt

On Windows:

    conda create \
        --channel conda-forge \
        -p .condaenv \
        --file requirements.d\pytest-windows.txt

## Testing

On Linux:

    ./.condaenv/bin/python -m pytest multisensor_pipeline

On macOS:

    ./.condaenv/bin/python -m pytest multisensor_pipeline

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
