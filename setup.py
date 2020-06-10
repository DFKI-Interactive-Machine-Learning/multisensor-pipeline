from distutils.core import setup
from setuptools import find_packages
import setuptools

setup(
    name='multisensor-pipeline',
    version='1.2.0',
    author='Michael Barz',
    author_email='michael.barz@dfki.de',
    license='CC BY-NC-SA 4.0',
    packages=find_packages(
        include=('multisensor_pipeline.*', 'multisensor_pipeline')
    ),
    url="",
    description="The core library of the DFKI multisensor pipeline framework.",
    python_requires='>=3.6.0',
    install_requires=[
        'requests',
        'pyzmq',
        'PyAudio',
        'networkx',
        'numpy',
        'Pillow'
    ],
    extras_require={
        'myo':  ['myo-python==0.2.2']
    },
    keywords=['multimodality', 'streaming', 'multisensor', 'sensors', 'multimodal interaction', 'pipeline'],
    classifiers=[
        "Framework :: DFKI Multisensor Pipeline"
    ]
)
