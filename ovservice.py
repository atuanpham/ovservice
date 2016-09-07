import click
import os
import shlex
import subprocess

basic_services = ['activemq', 'mongodb', 'ovclient', 'tomcat']
other_services = ['sip', 'vmmanager', 'scheduler']

@click.group()
def cli():
    pass

@click.command()
@click.argument('service', type=click.Choice(basic_services + other_services))
def start(service):
    click.echo('Starting %s service...' % service)

cli.add_command(start)
