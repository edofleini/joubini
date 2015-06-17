#!/usr/bin/env python

import base64
import boto.dynamodb
from boto.dynamodb.condition import *
from boto.exception import DynamoDBResponseError
import json
import os
import time

HASH_KEY = 'JOUBINI_ENVIRONMENT_NAME'

# not tested
def get_joubini_table(region='us-east-1', read_throughput=1, write_throughput=1, **kwargs):
    ddb = boto.dynamodb.connect_to_region(region_name=region)
    try:
        # get_table output is a DDB Table object
        return ddb.get_table(name='joubini')
        # If the table doesn't exist, an error will get thrown
    except DynamoDBResponseError as e:
        schema = ddb.create_schema(
            hash_key_name=HASH_KEY,
            hash_key_proto_value=str,
                )
        # create_table output is a DDB Table object
        return ddb.create_table(name='joubini', schema=schema, read_units=read_throughput, write_units=write_throughput)

# not tested
def load_env(env, region='us-east-1', keys=None, **kwargs):
    table = get_joubini_table(region=region)
    try:
        return table.get_item(hash_key=env, attributes_to_get=keys)
    except:
        return table.new_item(attrs={HASH_KEY:env})

# not tested
def list_envs(region='us-east-1', **kwargs):
    table = get_joubini_table(region=region)
    return [item[HASH_KEY] for item in table.scan(attributes_to_get=[HASH_KEY])]

# not tested
def get(env, key, region='us-east-1', **kwargs):
    return load_env(env=env, region=region, keys=[key]).get(key)

# not tested
def set(env, key, value, region='us-east-1', env_row = None, **kwargs):
    if key == HASH_KEY:
        raise Exception('Cannot use set to change the {0} attribute.'.format(HASH_KEY))
    env_row = env_row if env_row else load_env(env=env, region=region)
    env_row[key] = value
    env_row.save()

# not tested
def unset(env, key, region='us-east-1', **kwargs):
    if key == HASH_KEY:
        raise Exception('Cannot use unset to change the {0} attribute.'.format(HASH_KEY))
    env_row = load_env(env=env, region=region)
    env_row.delete_attribute(attr_name=key)
    env_row.save()

# not tested
def import_environment_from_joubini(env=None, region='us-east-1', ignore=[], **kwargs):
    env = env if env else os.environ.get(HASH_KEY, None)
    if not env:
        raise Exception('For import_environment_from_joubini, env must either be provided as a parameter or stored as an environment variable in {0}.'.format(HASH_KEY))
    env_row = load_env(env=env, region=region)
    for key in env_row.keys():
        if key not in ignore:
            os.environ[key]=env_row[key]

# not tested
def export_environment_to_joubini(env=None, region='us-east-1', ignore=[], **kwargs):
    env = env if env else os.environ.get(HASH_KEY, None)
    if not env:
        raise Exception('For export_environment_to_joubini, env must either be provided as a parameter or stored as an environment variable in {0}.'.format(HASH_KEY))
    env_row = load_env(env=env, region=region)
    for key in os.environ.keys():
        if not key in ignore + [HASH_KEY]:
            set(env=env, key=key, value=os.environ[key], env_row=env_row, region=region)
