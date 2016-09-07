import click
import os
import shlex
import subprocess

basic_services = ['activemq', 'mongodb', 'ovclient', 'tomcat']
other_services = ['sip', 'vmmanager', 'scheduler']

NG_HOME = os.environ['NG_HOME']
WRAPPER_CMD = NG_HOME + '/bin/wrapper/wrapper'
SERVICES_DIR = NG_HOME + '/services'

LOG_DIR = '/tmp/ovservice'

def create_dir(dirname):
    try:
        os.makedirs(dirname)
    except OSError:
        pass

def get_service_log_dir(service_name):
    return LOG_DIR + '/' + service_name

def get_service_pid_file(service_name):
    service_log_dir= get_service_log_dir(service_name)
    return service_log_dir + '/pid'

def get_service_log_file(service_name):
    service_log_dir = get_service_log_dir(service_name)
    return service_log_dir + '/' + service_name + '.log'

def get_service_pid(service_name):
    pid = None
    service_pid_file = get_service_pid_file(service_name)
    try:
        with open(service_pid_file, 'r') as pid_file:
            pid = int(pid_file.read())
    except IOError:
        pass
    return pid

def is_existed_service(service_name):
    pid = get_service_pid(service_name)
    if pid != None:
        return True
    return False

def store_pid(service_name, pid):
    service_pid_file = get_service_pid_file(service_name)
    with open(service_pid_file, 'w') as pid_file:
        pid_file.write(str(pid))

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
    create_dir(LOG_DIR)

@click.command()
@click.argument('service', type=click.Choice(basic_services + other_services))
def start(service):
    click.echo('Starting %s service...' % service)

    service_log_dir = get_service_log_dir(service)
    create_dir(service_log_dir)

    if is_existed_service(service):
        return

    if service == 'mongodb':
        pid = start_mongodb()

    store_pid(service, pid)

    click.echo('%s is started.' % service)

#------------------------------------------------------------------------------#
cli.add_command(start)
