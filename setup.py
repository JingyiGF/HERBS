"""
@author: Jingyi GF{jingyi.g.fuglstad@gmail.com}
"""

from setuptools import setup
from herbs import __VERSION__
import os

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "herbs",
    version = __VERSION__,
    author = "Jingyi GF",
    author_email = "jingyi.g.fuglstad@gmail.com",
    description="",
    keywords = "herbs",
    url = "https://github.com/JingyiGF/HERBS",
    packages = ['herbs'],
    long_description = read('README.md')
)