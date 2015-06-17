#!/usr/bin/env python

import argparse
import joubini.utils as joubini
import os

class CLIDispatcher:

    operation_info={
        'list_environments':{
            'help':'List the stored environments.',
            'initial':'l'
            },
        'print_environment':{
            'help':'Print all entries in the specified environment.',
            'initial':'p'
            },
        'export_environment':{
            'help':'Print all entries in the specified environment in a format that can exec\'d to add them to the Linux environment.  Run the command in backticks (`joubini -x -e foo`) in order to do this.',
            'initial':'x'
            },
        'import_environment':{
            'help':'Store all entries in the current Linux environment to the provided joubini env.  Any variables that are currently in joubini will be overwritten.',
            'initial':'i'
            },
        'get':{
            'help':'Get the specified environment variable.',
            'initial':'g'
            },
        'set':{
            'help':'Set the specified environment variable.',
            'initial':'s'
            },
        'unset':{
            'help':'Clear the specified environment variable.',
            'initial':'u'
            },
        'delete':{
            'help':'Delete the specified environment.',
            'initial':'d'
            },
        }

    def list_environments(self, **kwargs):
        envs = joubini.list_envs(**kwargs)
        for env in envs:
            print(env)

    def print_environment(self, **kwargs):
        env = joubini.load_env(**kwargs)
        max_length = max([len(key) for key in env.keys()])
        spacing = max_length + 2
        keys = env.keys()
        keys.remove(joubini.HASH_KEY)
        keys.insert(0, joubini.HASH_KEY)
        for key in keys:
            header = key + ': '
            spacer = ' ' * (spacing - len(header))
            print('{0}{1}{2}'.format(header,spacer,env[key]))

    def export_environment(self, **kwargs):
        env = joubini.load_env(**kwargs)
        max_length = max([len(key) for key in env.keys()])
        spacing = max_length + 2
        keys = env.keys()
        keys.remove(joubini.HASH_KEY)
        keys.insert(0, joubini.HASH_KEY)
        for key in keys:
            print('export {0}={1}'.format(key,env[key]))

    def import_environment(self, **kwargs):
        env = os.environ
        del kwargs['key']
        del kwargs['value']
        for key in env.keys():
            if not key in kwargs['ignore']:
                joubini.set(key=key, value=env[key], **kwargs)

    def get(self, **kwargs):
        print(joubini.get(**kwargs))

    def set(self, **kwargs):
        joubini.set(**kwargs)

    def unset(self, **kwargs):
        joubini.unset(**kwargs)

    def delete(self, **kwargs):
        env = kwargs['env']
        print('Not yet implemented.')
        exit(1)

    def get_argument_parser(self):
        parser = argparse.ArgumentParser(description='Interact with joubini from the command line.')
        operations = parser.add_mutually_exclusive_group(required=True)

        for operation in self.operation_info.keys():
            op = self.operation_info[operation]
            operation_cli = '--{0}'.format(operation.replace('_','-'))
            if op['initial']:
                operations.add_argument('-{0}'.format(op['initial']), operation_cli, action='store_true', help='Operation: {0}'.format(op['help']))
            else:
                operations.add_argument(operation_cli, action='store_true', help='Operation: {0}'.format(op['help']))

        parser.add_argument('-r', '--region', default='us-east-1', help='Argument: The AWS region to use.')
        parser.add_argument('-e', '--env', default=None, help='Argument: The name of the environment.')
        parser.add_argument('-k', '--key', default=None, help='Argument: The name of the variable to store.')
        parser.add_argument('-v', '--value', default=None, help='Argument: The value of the variable to store.')
        parser.add_argument('--ignore', default=[joubini.HASH_KEY], nargs='+', help='Argument: Environment variables to ignore.  Only used by import-environment.')
        parser.add_argument('-f', '--force', action='store_true', help='Argument: Skip normal confirmation prompts.  Optional for all calls.  May or may not do anything depending on whether or not I\'ve implemented it.')
        parser.add_argument('--verbose', action='store_true', help='Argument: Print random usually-useless information.  May or may not print anything depending on whether or not I\'ve implemented it yet, as I haven\'t right now.  Optional for all calls.')

        return parser

    def handle_args(self, args):
        operation = None
        argdict = {}
        for pair in args._get_kwargs():
            if pair[0] in self.operation_info.keys():
                operation = operation if not pair[1] else pair[0]
            else:
                argdict[pair[0]] = pair[1]
        try:
            getattr(self, operation)(**argdict)
        except Exception as e:
            print(e.message)
            exit(1)

    def do_stuff(self):
        parser = self.get_argument_parser()
        args = parser.parse_args()
        self.handle_args(args)
