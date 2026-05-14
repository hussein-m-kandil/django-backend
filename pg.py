#!/usr/bin/env python3

import argparse
import subprocess
from enum import Enum


class Command(str, Enum):
    up = 'docker compose up'
    stop = 'docker compose stop'
    config = 'docker compose config'
    down = 'docker compose down --remove-orphans'
    reset = down + ' --volumes'

    @classmethod
    def get_arg_name(cls):
        return cls.__name__.lower()

    @classmethod
    def choices(cls):
        return list(cls.__members__.keys())


arg_name = Command.get_arg_name()

parser = argparse.ArgumentParser(
    prog='PG',
    description=(
        'Run, stop, and tear-down a PostgreSQL database via the Docker Compose.'
        + '\nYou can pass any Docker CL options after --.'
    ),
)

parser.add_argument(
    arg_name,
    choices=Command.choices(),
    help='An action to take against the PG-DB via docker-compose.',
)

args, extra_args = parser.parse_known_args()

docker_cl_opts = ''

if extra_args:
    try:
        delimiter_index = extra_args.index('--')
        docker_cl_opts = ' '.join(extra_args[delimiter_index + 1 :])
    except ValueError:
        pass

pg_cmd = getattr(args, arg_name)
docker_cmd = getattr(Command, pg_cmd) + ' ' + docker_cl_opts

subprocess.run('python3 --version', shell=True)
exit(subprocess.run(docker_cmd, shell=True).returncode)
