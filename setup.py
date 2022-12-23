"""
@author: Jingyi GF{jingyi.g.fuglstad@gmail.com}
"""
import os
import sys
from sys import platform
from setuptools import setup, find_packages


is_problematic = False

if sys.version_info[:2] < (3, 8) or sys.version_info[:2] > (3, 11):
    is_problematic = True

if sys.version_info.minor == 8 and sys.version_info.micro < 10:
    is_problematic = True

if sys.version_info.minor == 9 and sys.version_info.micro == 0:
    is_problematic = True

if sys.version_info.minor == 10 and sys.version_info.micro >= 5:
    is_problematic = True

if is_problematic:
    raise RuntimeError("Python version >= 3.8.10 < 3.10.5 / 3.9.0 required.")

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
PyQt5 >= 5.14.2; python_version == "3.8"
PyQt5 >= 5.15.1; python_version == "3.9"
PyQt5 >= 5.15.5; python_version == "3.10"
pyqtgraph == 0.12.3
PyOpenGL >= 3.1.5
QtRangeSlider == 0.1.5
opencv-python >= 4.5.4.60
numba >= 0.54.1
numpy >= 1.20.3
scipy >= 1.7.3
requests >= 2.26.0
nibabel >= 3.2.1
pynrrd >= 0.4.3
tifffile >= 2021.11.2
aicspylibczi >= 3.0.3
pandas >= 1.3.5
natsort >= 8.0.2
imagecodecs >= 2022.2.22
h5py >= 3.7.0
tables >= 3.7.0
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
qss/*.qss
"""


setup(
    name="herbs",
    version="0.2.2",
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
