import os

from setuptools import setup, find_packages

from clashcallerbotreddit import __version__

version = __version__

module_dir = os.path.dirname(os.path.abspath(__file__)) + '/'

# Get requirements from requirements.txt
with open(module_dir + 'requirements.txt', 'r') as reqf:
    requirements = reqf.read().splitlines()

# Use README as long description
with open(module_dir + 'README.rst', 'r') as readf:
    long_description = readf.read()

setup(
    name='clashcallerbot-reddit',
    version=version,
    package_dir={'': 'clashcallerbotreddit'},
    packages=find_packages('clashcallerbotreddit'),
    scripts=['clashcallerbotreddit/reply.py', 'clashcallerbotreddit/search.py', 'clashcallerbotreddit/database.py'],

    install_requires=requirements,

    package_data={
        # If any package contains *.rst files, include them:
        '': ['*.rst']
    },

    # metadata to display on PyPI
    author='Jose A. Lerma III',
    author_email='jose@JoseALerma.com',
    description='Bot to help plan Clan Wars in reddit.',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    license='MIT',
    keywords='reddit PRAW ClashOfClans',
    url='http://clashcallerbotreddit.JoseALerma.com/',
    project_urls={
        'Documentation': 'https://josealermaiii.github.io/clashcallerbot-reddit',
        'Source Code': 'https://github.com/JoseALermaIII/clashcallerbot-reddit',

    },
    entry_points={
        'console_scripts': [
            'reply = clashcallerbotreddit.reply:main',
            'search = clashcallerbotreddit.search:main',
            'database = clashcallerbotreddit.database:main'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Devlopers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Linux',
        'Programming Language :: Python :: 3.6',
    ],
)
