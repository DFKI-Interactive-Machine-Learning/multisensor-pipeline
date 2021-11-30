"""Packaging logic for Multisensor Pipeline."""

from distutils.core import setup
from setuptools import find_packages

setup(
    name='multisensor-pipeline',
    version='2.0.0',
    author='Michael Barz',
    author_email='michael.barz@dfki.de',
    license='CC BY-NC-SA 4.0',
    packages=find_packages(
        include=('multisensor_pipeline.*', 'multisensor_pipeline')
    ),
    url="https://github.com/" +
        "DFKI-Interactive-Machine-Learning/multisensor-pipeline",
    description="The core library of the DFKI multisensor pipeline framework.",
    python_requires='>=3.6.0',
    install_requires=[
        'decorator<5.0.0',  # For networkx
        'networkx',
        'numpy',     # For Python 3.6
        'Pillow',
        'PyAudio',
        'pynput',
        'pyzmq',
        'av',
        'opencv-python',
    ],
    keywords=[
        'multimodality', 'streaming', 'multisensor', 'sensors',
        'multimodal interaction', 'pipeline', 'stream processing',
        'multiprocessing',
    ]
)
