#! python3
# -*- coding: utf-8 -*-
"""Defines logging dictionary.

Module defines dictionary for logging.config.dictConfig()
"""

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
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'filename': 'clashcaller.log',
            'maxBytes': 104857600,
            'backupCount': 3,
            'formatter': 'detailed'
        }
    },
    'loggers': {
        'root': {
            'level': 'NOTSET',
            'handlers': ['console', 'file']
        },
        'reply': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': 0,
            'qualname': 'reply'
        },
        'search': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': 0,
            'qualname': 'search'
        },
        'database': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': 0,
            'qualname': 'database'
        }
    }
}
