"""
AUTHOR NOTE: This is a test setup file to determine whether
https://github.com/fsaemi/evpy can be used a simple install.

Resources used:
https://github.com/NeuralNine/vidstream
https://youtu.be/tEFkHEKypLI
"""

from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

# PLACEHOLDER INFORMATION - DISREGARD UNTIL FIXED
VERSION = '0.0.01'
DESCRIPTION = 'evpy library setup test'
LONG_DESCRIPTION = 'evpy library setup test'

setup( # PLACEHOLDER INFORMATION - DISREGARD UNTIL FIXED
    name="evpy",
    version=VERSION,
    author="N/A",
    author_email="<noahvanous@tamu.edu>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/fsaemi/evpy",
    packages=find_packages(),
    install_requires=['matplotlib', 'numpy', 'scipy'],
    keywords=['python'],
    classifiers=[
        "Placeholder",
    ]
)
