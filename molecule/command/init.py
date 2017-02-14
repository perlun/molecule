#  Copyright (c) 2015-2017 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

import os

import click
import cookiecutter
import cookiecutter.main

from molecule import config
from molecule import logger
from molecule import util

LOG = logger.get_logger(__name__)


def _process_templates(template_dir, extra_context, output_dir,
                       overwrite=True):
    """
    Process templates as found in the named directory.

    :param template_dir: A string containing an absolute or relative path to a
     directory where the templates are located. If the provided directory is a
     relative path, it is resolved using a known location.
    :param extra_context: A dict of values that are used to override default
     or user specified values.
    :param output_dir: An string with an absolute path to a directory where the
     templates should be written to.
    :param overwrite: An optional bool whether or not to overwrite existing
     templates.
    :return: None
    """
    template_dir = _resolve_template_dir(template_dir)

    cookiecutter.main.cookiecutter(
        template_dir,
        extra_context=extra_context,
        output_dir=output_dir,
        overwrite_if_exists=overwrite,
        no_input=True, )


def _resolve_template_dir(template_dir):
    if not os.path.isabs(template_dir):
        template_dir = os.path.join(
            os.path.dirname(__file__), os.path.pardir, 'cookiecutter',
            template_dir)

    return template_dir


def _init_new_role(command_args):
    """
    >>> molecule init role --role-name foo
    """
    role_name = command_args['role_name']
    role_directory = os.getcwd()
    LOG.info('Initializing new role {}...'.format(role_name))

    if os.path.isdir(role_name):
        msg = ('The directory {} exists. '
               'Cannot create new role.').format(role_name)
        util.sysexit_with_message(msg)

    _process_templates('role', command_args, role_directory)
    scenario_base_directory = os.path.join(role_directory, role_name)
    templates = [
        'scenario/driver/{driver_name}'.format(**command_args),
        'scenario/verifier/{verifier_name}'.format(**command_args)
    ]
    for template in templates:
        _process_templates(template, command_args, scenario_base_directory)

    role_directory = os.path.join(role_directory, role_name)
    msg = 'Initialized role in {} successfully.'.format(role_directory)
    LOG.success(msg)


def _init_new_scenario(command_args):
    """
    >>> molecule init scenario --scenario-name default --role-name foo
    """
    scenario_name = command_args['scenario_name']
    role_name = os.getcwd().split(os.sep)[-1]
    role_directory = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

    LOG.info('Initializing new scenario {}...'.format(scenario_name))
    molecule_directory = config.molecule_directory(
        os.path.join(role_directory, role_name))
    scenario_directory = os.path.join(molecule_directory, scenario_name)
    scenario_base_directory = os.path.dirname(scenario_directory)

    if os.path.isdir(scenario_directory):
        msg = ('The directory molecule/{} exists. '
               'Cannot create new scenario.').format(scenario_name)
        util.sysexit_with_message(msg)

    scenario_base_directory = os.path.join(role_directory, role_name)
    templates = [
        'scenario/driver/{driver_name}'.format(**command_args),
        'scenario/verifier/{verifier_name}'.format(**command_args)
    ]
    for template in templates:
        _process_templates(template, command_args, scenario_base_directory)

    role_directory = os.path.join(role_directory, role_name)
    msg = 'Initialized scenario in {} successfully.'.format(scenario_directory)
    LOG.success(msg)


@click.group()
def init():
    """ Initialize a new role or scenario. """


@init.command()
@click.option(
    '--dependency-name',
    type=click.Choice(['galaxy']),
    default='galaxy',
    help='Name of dependency to initialize. (galaxy)')
@click.option(
    '--driver-name',
    type=click.Choice(['docker', 'lxc', 'lxd', 'vagrant']),
    default='docker',
    help='Name of driver to initialize. (docker)')
@click.option(
    '--lint-name',
    type=click.Choice(['ansible-lint']),
    default='ansible-lint',
    help='Name of lint to initialize. (ansible-lint)')
@click.option(
    '--provisioner-name',
    type=click.Choice(['ansible']),
    default='ansible',
    help='Name of provisioner to initialize. (ansible)')
@click.option('--role-name', required=True, help='Name of the role to create.')
@click.option(
    '--verifier-name',
    type=click.Choice(['goss', 'testinfra']),
    default='testinfra',
    help='Name of verifier to initialize. (testinfra)')
def role(dependency_name, driver_name, lint_name, provisioner_name, role_name,
         verifier_name):  # pragma: no cover
    """ Initialize a new role for use with Molecule. """
    command_args = {
        'dependency_name': dependency_name,
        'driver_name': driver_name,
        'lint_name': lint_name,
        'provisioner_name': provisioner_name,
        'role_name': role_name,
        'scenario_name': 'default',
        'subcommand': __name__,
        'verifier_name': verifier_name
    }

    _init_new_role(command_args)


@init.command()
@click.option(
    '--driver-name',
    type=click.Choice(['docker', 'lxc', 'lxd', 'vagrant']),
    default='docker',
    help='Name of driver to initialize. (docker)')
@click.option('--role-name', required=True, help='Name of the role to create.')
@click.option(
    '--scenario-name', required=True, help='Name of the scenario to create.')
@click.option(
    '--verifier-name',
    type=click.Choice(['goss', 'testinfra']),
    default='testinfra',
    help='Name of verifier to initialize. (testinfra)')
def scenario(driver_name, role_name, scenario_name,
             verifier_name):  # pragma: no cover
    """ Initialize a new scenario for use with Molecule. """
    command_args = {
        'driver_name': driver_name,
        'role_name': role_name,
        'scenario_name': scenario_name,
        'subcommand': __name__,
        'verifier_name': verifier_name
    }

    _init_new_scenario(command_args)
