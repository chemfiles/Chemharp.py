"""
Move the .tar.bz2 file generated by conda to the current directory
"""
import os
import glob
import shutil
from conda_build.config import config

binary_package_glob = os.path.join(config.bldpkgs_dir, 'chemharp*.tar.bz2')
binary_package = glob.glob(binary_package_glob)[0]

shutil.move(binary_package, '.')