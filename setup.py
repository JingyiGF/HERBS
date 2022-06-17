"""
@author: Jingyi GF{jingyi.g.fuglstad@gmail.com}
"""
import os
from setuptools import setup, find_packages
exec(open('herbs/version.py').read())


# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="herbs",
    version=__version__,
    author="Jingyi GF",
    author_email="jingyi.g.fuglstad@gmail.com",
    description="",
    keywords="brain atlas, histological image registration, probe coordinates",
    url="https://github.com/JingyiGF/HERBS",
    packages=find_packages(exclude=[]),
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    project_urls={
        "Bug Tracker": "https://github.com/JingyiGF/HERBS/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
