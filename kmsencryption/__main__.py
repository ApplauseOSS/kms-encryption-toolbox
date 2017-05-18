import aws_encryption_sdk
import base64
import botocore.session
import click
import os


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
    click.echo(prefix + result)


@main.command(help='Decrypts a base64-encoded data.')
@click.option('--data', 'data', envvar='DATA', help='Data to be decrypted. Use to pass it as a named argument.')
@click.option('--env', 'env', help='Name of an environment variable that contains data to be decrypted.')
@click.option('--profile', 'profile', default=None, help='Name of an AWS CLI profile to be used when contacting AWS.')
@click.option('--prefix', 'prefix', default='', help='An input prefix to be trimmed from the beginning before a value is decrypted.')
def decrypt(data, env, profile, prefix):
    kms_key_provider = get_key_provider(None, profile)
    if env is not None:
        data = os.getenv(env, data)
    if not data:
        raise ValueError('No data provided via --data or in a variable name passed with --env')

    if data.startswith(prefix):
        data = data[len(prefix):]

    raw_data = base64.b64decode(data)
    decrypted_plaintext, decryptor_header = aws_encryption_sdk.decrypt(
        source=raw_data,
        key_provider=kms_key_provider)
    click.echo(decrypted_plaintext)


if __name__ == '__main__':
    main()
