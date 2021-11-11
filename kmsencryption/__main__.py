
from kmsencryption import lib

import click
import sys


@click.group(context_settings={"help_option_names": ['-h', '--help']})
def main():
    pass


@main.command(help='Encrypts data with a new data key and returns a base64-encoded result.')
@click.option('--cmk-arn', 'cmk_arn', prompt=True, help='ARN of an existing Customer Master Key in KMS')
@click.option('--data', 'data', envvar='DATA', help='Data to be encrypted. Use to pass it as a named argument.')
@click.option('--env', 'env', help='Name of an environment variable that contains data to be encrypted.')
@click.option('--file', 'path', help='Path to a file to be encrypted')
@click.option('--profile', 'profile', default=None, help='Name of an AWS CLI profile to be used when contacting AWS.')
@click.option('--prefix', 'prefix', default='', help='An output prefix to be added to the generated result.')
def encrypt(cmk_arn, data, env, path, profile, prefix):
    click.echo(lib.encrypt(cmk_arn, data, env, path, profile, prefix))


@main.command(help='Decrypts a base64-encoded data.')
@click.option('--data', 'data', envvar='DATA', help='Data to be decrypted. Use to pass it as a named argument.')
@click.option('--env', 'env', help='Name of an environment variable that contains data to be decrypted.')
@click.option('--file', 'path', help='Path to a file to be decrypted')
@click.option('--profile', 'profile', default=None, help='Name of an AWS CLI profile to be used when contacting AWS.')
@click.option('--prefix', 'prefix', default='',
              help='An input prefix to be trimmed from the beginning before a value is decrypted.')
@click.option('--no-newline', 'no_newline', is_flag=True, default=False, help='Disable implicit newline for decrypted output')
def decrypt(data, env, path, profile, prefix, no_newline):
    click.echo(lib.decrypt(data, env, path, profile, prefix), nl=(False if no_newline else True))


@main.command('decrypt-json',
              help='Accepts a JSON map in STDIN (or a file provided in the INPUT parameter) and '
                   'decrypts base64-encoded string values inside of it.')
@click.argument('input', type=click.File('rb'), default=sys.stdin)
@click.option('--profile', 'profile', default=None, help='Name of an AWS CLI profile to be used when contacting AWS.')
@click.option('--prefix', 'prefix', default='',
              help='An input prefix to be trimmed from the beginning before a value is decrypted.')
@click.option('--allow-partial', default=False, is_flag=True,
              help='If partially encrypted string values inside JSON are allowed. Substrings to decrypt are ' +
              'identified by the starting prefix and end with a whitespace or end of string.')
def decrypt_json(input, profile, prefix, allow_partial):
    click.echo(lib.decrypt_json(input, profile, prefix, allow_partial))


@main.command('encrypt-json',
              help='Accepts a JSON map in STDIN (or a file provided in the INPUT parameter) and '
                   'encrypts values inside of it then saves base64-encoded.')
@click.argument('input', type=click.File('rb'), default=sys.stdin)
@click.option('--cmk-arn', 'cmk_arn', prompt=True, help='ARN of an existing Customer Master Key in KMS')
@click.option('--profile', 'profile', default=None, help='Name of an AWS CLI profile to be used when contacting AWS.')
@click.option('--prefix', 'prefix', default='',
              help='An output prefix to be added to the beginning of an encrypted value.')
def encrypt_json(input, cmk_arn, profile, prefix):
    click.echo(lib.encrypt_json(input, cmk_arn, profile, prefix))


if __name__ == '__main__':
    main()
