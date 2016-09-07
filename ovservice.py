import click
import os
import shlex
import subprocess

basic_services = ['activemq', 'mongodb', 'ovclient', 'tomcat']
other_services = ['sip', 'vmmanager', 'scheduler']

NG_HOME = os.environ['NG_HOME']
WRAPPER_CMD = NG_HOME + '/bin/wrapper/wrapper'
SERVICES_DIR = NG_HOME + '/services'

TEMP_DIR = '/tmp/ovservice'

def create_dir(dirname):
    try:
        os.makedirs(dirname)
    except OSError:
        pass

def run_command(cmd):
    args = shlex.split(cmd)
    with open(os.devnull, 'w') as devnull:
        process = subprocess.Popen(args, stdout=devnull, stderr=subprocess.STDOUT)
    return process.pid


def start_mongodb():
    MONGO_CONFIG = '--config ' + SERVICES_DIR + '/mongodb/mongodb.conf'
    MONGO_CMD = SERVICES_DIR + '/mongodb/bin/mongod'
    cmd = MONGO_CMD + ' ' + MONGO_CONFIG
    return run_command(cmd)

@click.group()
def cli():
    create_dir(TEMP_DIR)

@click.command()
@click.argument('service', type=click.Choice(basic_services + other_services))
def start(service):
    click.echo('Starting %s service...' % service)
    TEMP_SERVICE_DIR = TEMP_DIR + '/' + service
    PID_LOG = TEMP_SERVICE_DIR + '/pid'
    create_dir(TEMP_SERVICE_DIR)
    pid = None

    try:
        with open(PID_LOG, 'r') as pid_log:
            pid = int(pid_log.read())
    except IOError:
        pass

    if service == 'mongodb':
        pid = start_mongodb()

    with open(PID_LOG, 'w') as pid_log:
        pid_log.write(str(pid))

cli.add_command(start)
