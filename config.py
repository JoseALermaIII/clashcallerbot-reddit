"""Loads database.ini for use in clashcallerbot_database.py"""
import os
import sys
import configparser

# Read database.ini file and make database instance
config = configparser.ConfigParser()
module_dir = os.path.dirname(sys.modules[__name__].__file__)
locations = [os.path.join(module_dir, 'database.ini'), 'database.ini']
config.read(locations)
