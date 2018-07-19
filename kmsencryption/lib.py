from future.utils import iteritems
from future.utils import string_types

import aws_encryption_sdk
import base64
import botocore.session
import json
import os


def get_key_provider(cmk_arn, profile):
    if cmk_arn:
        kms_kwargs = dict(key_ids=[cmk_arn])
    else:
        kms_kwargs = dict()
    if profile is not None:
        kms_kwargs['botocore_session'] = botocore.session.Session(profile=profile)
    return aws_encryption_sdk.KMSMasterKeyProvider(**kms_kwargs)


def decrypt_value(data, prefix, key_provider):
    if data.startswith(prefix):
        data = data[len(prefix):]

    raw_data = base64.b64decode(data)
    decrypted_plaintext, decryptor_header = aws_encryption_sdk.decrypt(
        source=raw_data,
        key_provider=key_provider)
    return decrypted_plaintext


def encrypt_value(data, prefix, key_provider):
    ciphertext, encryptor_header = aws_encryption_sdk.encrypt(
        source=data,
        key_provider=key_provider)
    return prefix + base64.b64encode(ciphertext).decode('utf-8')


def encrypt(cmk_arn, data, env, profile, prefix):
    key_provider = get_key_provider(cmk_arn, profile)
    if env is not None:
        data = os.getenv(env, data)
    if not data:
        raise ValueError('No data provided via --data or in a variable name passed with --env')

    return encrypt_value(data, prefix, key_provider)


def decrypt(data, env, profile, prefix):
    key_provider = get_key_provider(None, profile)
    if env is not None:
        data = os.getenv(env, data)
    if not data:
        raise ValueError('No data provided via --data or in a variable name passed with --env')

    return decrypt_value(data, prefix, key_provider)


def decrypt_object(input_object, prefix, key_provider):
    if not input_object:
        return input_object
    if isinstance(input_object, string_types):
        output = decrypt_value(input_object, prefix, key_provider) if input_object.startswith(prefix) else input_object
        return output.decode('utf-8')
    if isinstance(input_object, dict):
        output = {}
        for name, value in iteritems(input_object):
            output[name] = decrypt_object(value, prefix, key_provider)
        return output
    if isinstance(input_object, list):
        output = []
        for value in input_object:
            output.append(decrypt_object(value, prefix, key_provider))
        return output
    return input_object


def decrypt_json(json_input, profile, prefix):
    key_provider = get_key_provider(None, profile)
    input_object = json.load(json_input)
    output = decrypt_object(input_object, prefix, key_provider)
    return json.dumps(output)


def encrypt_json(json_input, cmk_arn, profile, prefix):
    key_provider = get_key_provider(cmk_arn, profile)
    input_map = json.load(json_input)
    output = {}
    for name, value in iteritems(input_map):
        output[name] = encrypt_value(value, prefix, key_provider)
    return json.dumps(output)
