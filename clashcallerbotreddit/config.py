#! python3
# -*- coding: utf-8 -*-
"""Loads database.ini.

Module loads database.ini for use in database.py,
search.py, and reply.py.

Attributes:
    config (complex): A configparser.ConfigParser() object containing the sections
        inside database.ini
    module_dir (str): String with the absolute path of the module's directory.
    locations (list): List containing all possible paths of database.ini
"""

import os
import sys
import configparser

# Read database.ini file
config = configparser.ConfigParser()
module_dir = os.path.dirname(sys.modules[__name__].__file__)
locations = [os.path.join(module_dir, 'database.ini'), 'database.ini']
config.read(locations)
