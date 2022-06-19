"""
@author: Jingyi GF{jingyi.g.fuglstad@gmail.com}
"""
import os
import sys
import subprocess
import textwrap
import warnings
import builtins
import re
from setuptools import setup, find_packages

if sys.version_info[:2] < (3, 8) or sys.version_info[:2] > (3, 11):
    raise RuntimeError("Python version >= 3.8 < 3.11 required.")


# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


CLASSIFIERS = """
Development Status :: 3 - Alpha
Intended Audience :: Science/Research
Intended Audience :: Developers
Intended Audience :: Education
License :: OSI Approved :: MIT License
Programming Language :: Python :: 3
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
Programming Language :: Python :: 3.10
Programming Language :: Python :: 3 :: Only
Topic :: Software Development
Topic :: Scientific/Engineering
Typing :: Typed
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: Unix
Operating System :: MacOS
"""

REQUIRES = """
PyQt5 == 5.14.2
pyqtgraph == 0.12.3
PyOpenGL == 3.1.5
QtRangeSlider == 0.1.5
opencv-python
numba
numpy
scipy
shutil
requests
csv
nibabel
pynrrd
tifffile
aicspylibczi
pandas
natsort
imagecodecs
random
h5py
tables
"""


PACKAGE_DATA = """
main_window.ui
data/query.csv
data/atlas_labels.pkl
icons/*.svg
icons/*.png
icons/layers/*.svg
icons/layers/*.png
icons/sidebar/*.svg
icons/sidebar/*.png
icons/toolbar/*.svg
icons/toolbar/*.png
"""


setup(
    name="herbs",
    version="0.0.2",
    author="Jingyi GF",
    author_email="jingyi.g.fuglstad@gmail.com",
    description="A Python-based GUI for Histological E-data Registration in Brain Space",
    keywords="brain atlas, histological image registration, probe coordinates",
    url="https://github.com/JingyiGF/HERBS",
    packages=find_packages(),
    package_data={'': [_f for _f in PACKAGE_DATA.split('\n') if _f]},
    include_package_data=True,
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    project_urls={
        "Bug Tracker": "https://github.com/JingyiGF/HERBS/issues",
    },
    classifiers=[_f for _f in CLASSIFIERS.split('\n') if _f],
    python_requires=">=3.8",
    install_requires=[_f for _f in REQUIRES.split('\n') if _f]
)
