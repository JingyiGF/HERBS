import os
from os.path import dirname, realpath, join
import sys

from .herbsgui import main


def run_herbs():
    current_wd = os.getcwd()
    script_dir = dirname(realpath(__file__))
    os.chdir(script_dir)
    main()
    os.chdir(current_wd)
