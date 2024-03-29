from distutils.core import setup
from setuptools import find_packages

install_requires = [
    'decorator<5.0.0',  # For networkx
    'networkx>=2.5',
    'numpy>1.7.0',
    'Pillow>=8.3.2',
    'pynput>=1.7.3',
    'pyzmq>=20.0.0',
    'av>=8.0.1',
    'sounddevice>=0.4.3',
    'soundfile>=0.10.3',
    'msgpack>1.0.0',
    'windows-capture-devices; platform_system == "Windows"'
]

setup(
    name='multisensor-pipeline',
    version='2.1.1',
    author='Michael Barz',
    author_email='michael.barz@dfki.de',
    license='CC BY-NC-SA 4.0',
    packages=find_packages(
        include=('multisensor_pipeline.*', 'multisensor_pipeline')
    ),
    url="https://github.com/DFKI-Interactive-Machine-Learning/multisensor-pipeline",
    description="The core library of the DFKI multisensor pipeline framework.",
    python_requires='>=3.6.0',
    install_requires=install_requires,
    keywords=[
        'multimodality', 'streaming', 'multisensor', 'sensors', 'multimodal interaction',
        'pipeline', 'stream processing', 'multiprocessing'
    ]
)
