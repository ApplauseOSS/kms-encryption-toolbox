import aws_encryption_sdk
import base64
import botocore.session
import click
import json
import os
import sys


@click.group(context_settings={"help_option_names": ['-h', '--help']})
def main():
    pass


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


@main.command(help='Encrypts data with a new data key and returns a base64-encoded result.')
@click.option('--cmk-arn', 'cmk_arn', prompt=True, help='ARN of an existing Customer Master Key in KMS')
@click.option('--data', 'data', envvar='DATA', help='Data to be encrypted. Use to pass it as a named argument.')
@click.option('--env', 'env', help='Name of an environment variable that contains data to be encrypted.')
@click.option('--profile', 'profile', default=None, help='Name of an AWS CLI profile to be used when contacting AWS.')
@click.option('--prefix', 'prefix', default='', help='An output prefix to be added to the generated result.')
def encrypt(cmk_arn, data, env, profile, prefix):
    kms_key_provider = get_key_provider(cmk_arn, profile)
    if env is not None:
        data = os.getenv(env, data)
    if not data:
        raise ValueError('No data provided via --data or in a variable name passed with --env')

    my_ciphertext, encryptor_header = aws_encryption_sdk.encrypt(
        source=data,
        key_provider=kms_key_provider)
    result = base64.b64encode(my_ciphertext)
    click.echo(prefix + result.decode('utf-8'))


@main.command(help='Decrypts a base64-encoded data.')
@click.option('--data', 'data', envvar='DATA', help='Data to be decrypted. Use to pass it as a named argument.')
@click.option('--env', 'env', help='Name of an environment variable that contains data to be decrypted.')
@click.option('--profile', 'profile', default=None, help='Name of an AWS CLI profile to be used when contacting AWS.')
@click.option('--prefix', 'prefix', default='',
              help='An input prefix to be trimmed from the beginning before a value is decrypted.')
def decrypt(data, env, profile, prefix):
    kms_key_provider = get_key_provider(None, profile)
    if env is not None:
        data = os.getenv(env, data)
    if not data:
        raise ValueError('No data provided via --data or in a variable name passed with --env')

    click.echo(decrypt_value(data, prefix, kms_key_provider))


@main.command('decrypt-json',
              help='Accepts a JSON map in STDIN (or a file provided in the INPUT parameter) and '
                   'decrypts base64-encoded map values inside of it.')
@click.argument('input', type=click.File('rb'), default=sys.stdin)
@click.option('--profile', 'profile', default=None, help='Name of an AWS CLI profile to be used when contacting AWS.')
@click.option('--prefix', 'prefix', default='',
              help='An input prefix to be trimmed from the beginning before a value is decrypted.')
def decrypt_json(input, profile, prefix):
    kms_key_provider = get_key_provider(None, profile)
    input_map = json.load(input)
    output = {}
    for name, value in input_map.iteritems():
        output[name] = decrypt_value(value, prefix, kms_key_provider) if value.startswith(prefix) else value
    click.echo(json.dumps(output))


if __name__ == '__main__':
    main()
