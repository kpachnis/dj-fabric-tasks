import crypt
import os
from random import choice
from string import digits, letters

from fabric.api import env


PUNCTUATION = '!@#$%^&*(-_=+)'

env.roledefs = {
    'web': ['<hostname>'],
    'app': ['<hostname>'],
    'db': ['<hostname>']
}

env.forward_agent = True

env.password = '<password>'

env.app = '<app_name>'
env.app_path = '/u/apps/{}'.format(env.app)
env.service_account = env.app

env.deployer = {
    'account': '<username>',
    'password': crypt.crypt('test', 'Afe'),
    'key': open(os.path.abspath(os.path.join(os.getenv('HOME'), '.ssh', '<filename>.pub'))).read()
}

env.git = {
    'url': '<user>@<hostname>:<repo>.git',
    'branch': 'master'
}

env.db = {
    'name': '<db_name>',
    'user': '<db_user>',
    'password': '<db_password>',
    'host': '<db_host>',
    'port': None,
}

env.dba = {
    'user': '<dba_user>',
    'password': '<dba_password>'
}

env.sentry_dsn = '<get_sentry_url>'

env.secret_key = ''.join([choice(digits + letters + PUNCTUATION) for i in xrange(80)])

env.recaptcha = {
    'public_key': '<public_key>',
    'private_key': '<private_key>',
}

env.email = {
    'host': '<email_host>',
    'user': '<email_user>',
    'password': '<email_password>',
    'port': 587,
    'ssl': True,
}

env.newrelic_key = '<newrelic_key>'

