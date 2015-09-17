# -*- coding: utf-8 -*-
import os
from random import choice
from string import letters, digits
from ConfigParser import RawConfigParser

from fabric.api import task
from fabric.colors import red, green
from fabric.contrib import console


@task
def generate_key(length=80, project='project'):
    """
    Generate an N length string in the .secret_key.cfg file under the project directory.
    """

    secret_key = ''.join([choice(letters + digits + '!@#$%^&*()-_=+') for i in xrange(int(length))])
    secret_key_file = os.path.join(os.getcwd(), project, '.secret_key.cfg')

    if os.path.exists(secret_key_file):
        if console.confirm("File exists. Overwrite?"):
            pass
        else:
            print "Quitting..."
            exit(0)

    config = RawConfigParser()
    config.add_section(project)
    config.set(project, 'SECRET_KEY', secret_key)

    try:
        with open(secret_key_file, 'wb') as config_file:
            config.write(config_file)
            print(green("Key writter in %s") % secret_key_file)
    except IOError:
        print(red("Cannot write to file %s") % secret_key_file)
