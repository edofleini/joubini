#!/usr/bin/env python

import base64
import boto.dynamodb
from boto.dynamodb.condition import *
from boto.exception import DynamoDBResponseError
import json
import time

HASH_KEY = 'joubini-environment-name'

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
def get(env, key, region='us-east-1', **kwargs):
    return load_env(env=env, region=region, keys=[key]).get(key)

# not tested
def set(env, key, value, region='us-east-1', **kwargs):
    if key == HASH_KEY:
        raise Exception('Cannot use put_value to change the environment attribute.')
    env_row = load_env(env=env, region=region)
    env_row[key] = value
    env_row.save()
