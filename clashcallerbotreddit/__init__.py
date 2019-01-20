# clashcallerbot-reddit: Bot to help plan Clan Wars in reddit
# MIT License
# Jose A. Lerma III jose@JoseALerma.com

"""clashcallerbot-reddit constants

Contains constant variables used in source files.

Attributes:
    __version__ (str): String with version number using the `Semantic Versioning Scheme`_
    config (configparser.ConfigParser): A configparser object containing the sections inside database.ini
    module_dir (str): String with the absolute path of the module's directory.
    locations (list): List containing all possible paths of database.ini
    LOGGING (dict): Dictionary containing definitions for the loggers, handlers,
        and formatters.

.. _Semantic Versioning Scheme:
    https://semver.org/

"""

import os
import sys
import configparser

__version__ = '2.6.0'
__all__ = ['__version__', 'config', 'LOGGING']

# Loads database.ini for use in database.py, search.py, and reply.py.
config = configparser.ConfigParser()
module_dir = os.path.dirname(sys.modules[__name__].__file__)
package_dir = os.path.split(module_dir)[0] + '/'
locations = [os.path.join(package_dir, 'database.ini'), 'database.ini']
config.read(locations)

# Defines dictionary for logging.config.dictConfig()
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': 'F1 %(asctime)s %(name)-15s %(levelname)-8s %(message)s',
            'class': 'logging.Formatter'
        },
        'brief': {
            'format': 'F2 %(levelname)-8s: %(name)-15s: %(message)s',
            'class': 'logging.Formatter'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'stream': 'ext://sys.stdout',
            'formatter': 'brief'
        },
        'searchfile': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'filename': package_dir + 'logs/search.log',
            'maxBytes': 26214400,  # 25 MiB
            'backupCount': 3,
            'formatter': 'detailed'
        },
        'replyfile': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'filename': package_dir + 'logs/reply.log',
            'maxBytes': 26214400,  # 25 MiB
            'backupCount': 3,
            'formatter': 'detailed'
        },
        'databasefile': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'filename': package_dir + 'logs/database.log',
            'maxBytes': 26214400,  # 25 MiB
            'backupCount': 3,
            'formatter': 'detailed'
        },
    },
    'loggers': {
        'root': {
            'level': 'NOTSET',
            'handlers': ['console', 'searchfile']
        },
        'reply': {
            'level': 'DEBUG',
            'handlers': ['console', 'replyfile'],
            'propagate': 0,
            'qualname': 'reply'
        },
        'search': {
            'level': 'DEBUG',
            'handlers': ['console', 'searchfile'],
            'propagate': 0,
            'qualname': 'search'
        },
        'database': {
            'level': 'DEBUG',
            'handlers': ['console', 'databasefile'],
            'propagate': 0,
            'qualname': 'database'
        }
    }
}
