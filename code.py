# -*- coding: utf-8 -*-
from compileall import compile_file
from fnmatch import fnmatch
import os

from fabric.api import task


@task
def clean(directory):
    """
    Clean project python compiled files
    """

    for root, paths, files in os.walk(directory):
        for file in files:
            if fnmatch(file, '*.pyc'):
                try:
                    print "Removing file %s" % os.path.join(root, file)
                    os.remove(os.path.join(root, file))
                except OSError as e:
                    print e
                    exit(1)


@task
def compile(directory):
    """
    Compile project files
    """

    for root, paths, files in os.walk(directory):
        for file in files:
            if fnmatch(file, '*.py'):
                compile_file(os.path.join(root, file))
