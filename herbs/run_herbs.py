import os
from os.path import dirname, realpath, join
import sys


def run_herbs():
    script_dir = dirname(realpath(__file__))
    os.chdir(script_dir)
    print(script_dir)
    # os.system(join(script_dir, 'herbsgui.py'))
    exec(open('herbsgui.py').read())
    # runfile('/Users/jingyig/Work/Kavli/PyCode/Archived/HERBS/herbs/herbsgui.py',
    #         wdir='/Users/jingyig/Work/Kavli/PyCode/Archived/HERBS/herbs')