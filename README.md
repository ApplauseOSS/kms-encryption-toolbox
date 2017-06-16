# kms-encryption-toolbox
Encryption toolbox to be used with the Amazon Key Management Service for securing your deployment secrets.
It encapsulates the `aws-encryption-sdk` package to expose cmdline actions. For both `encrypt` and `decrypt` actions,
the library requests a new data key from KMS and encrypts it with the Customer Master Key. This encryption happens server-side and is performed by Amazon.

Whatever data you pass to be encrypted or decrypted, all the cryptographic computation happens on the client side, hence
your data is never sent over the wire. The `aws-encryption-sdk` guarantees embedding the data key used for sensitive data encryption
in the output stream that's being base64-encoded before returning from the `encrypt` command.

`decrypt` expects a data key to be embedded in the passed data. The data key is decrypted in KMS first (using the Customer Master Key)
and only then used to decrypt the sensitive data. As in case of `encrypt`, decryption also happens on the client side.

## pip
Package is available in the PyPI repo.

    $ pip install kms-encryption-toolbox
    
## Usage

### Encrypt
    
    $ kms-encryption encrypt --help
    
    Usage: kms-encryption encrypt [OPTIONS]
    Encrypts data with a new data key and returns a base64-encoded result.

    Options:
    --cmk-arn TEXT  ARN of an existing Customer Master Key in KMS
    --data TEXT     Data to be encrypted. Use to pass it as a named argument.
    --env TEXT      Name of an environment variable that contains data to be
                    encrypted.
    --profile TEXT  Name of an AWS CLI profile to be used when contacting AWS.
    --prefix TEXT   An output prefix to be added to the generated result.
    -h, --help      Show this message and exit.

### Decrypt

    $ kms-encryption decrypt --help 
    
    Usage: kms-encryption decrypt [OPTIONS]
    Decrypts a base64-encoded data.

    Options:
    --data TEXT     Data to be decrypted. Use to pass it as a named argument.
    --env TEXT      Name of an environment variable that contains data to be
                    decrypted.
    --profile TEXT  Name of an AWS CLI profile to be used when contacting AWS.
    --prefix TEXT   An input prefix to be trimmed from the beginning before a
                    value is decrypted.
    -h, --help      Show this message and exit.
    
### Decrypt a JSON map
    
    $ kms-encryption decrypt-json --help

    Usage: kms-encryption decrypt-json [OPTIONS] [INPUT]

    Accepts a JSON map passed via standard input (or a file provided in the INPUT parameter)
    and decrypts base64-encoded map values inside of it.

    Options:
    --profile TEXT  Name of an AWS CLI profile to be used when contacting AWS.
    --prefix TEXT   An input prefix to be trimmed from the beginning before a
                    value is decrypted.
    -h, --help      Show this message and exit.
    
    
### Encrypt a JSON map
    
    $ kms-encryption encrypt-json --help
    
    Usage: kms-encryption encrypt-json [OPTIONS] [INPUT]

    Accepts a JSON map in STDIN (or a file provided in the INPUT parameter)
    and encrypts values inside of it then saves base64-encoded.

    Options:
    --cmk-arn TEXT  ARN of an existing Customer Master Key in KMS
    --profile TEXT  Name of an AWS CLI profile to be used when contacting AWS.
    --prefix TEXT   An output prefix to be added to the beginning of an
                  encrypted value.
    -h, --help      Show this message and exit.


## Use examples

    $ export SECRET_VALUE="This is some super secret string"  
    $ export ENCRYPTED_VALUE=$(kms-encryption encrypt --cmk-arn arn:aws:kms:us-east-1:123456789012:key/1e1a6a81-93e0-4b9a-954b-aa1234567890 --env "SECRET_VALUE" --prefix "decrypt:")
    
    $ echo $ENCRYPTED_VALUE
    decrypt:AYADeJECDnf7+NLeAVJsur5YuekAXwABABVhd3MtY3J5cHRvLXB1YmxpYy1rZXkAREFnTHdvU1h5UVJuU3FkZGNsM0N3RXVXdURma1NYSG1KZThZZE9Wck1PUUgwMWgyRVV3U2xFK0VCamx4azVsd0EzQT09AAEAB2F3cy1rbXMAS2Fybjphd3M6a21zOnVzLWVhc3QtMTo4NzM1NTkyNjkzMzg6a2V5LzFlMWE2YTgxLTkzZTAtNGI5YS05NTRiLWNjMDk4MDJiZjNjZQC4AQICAHgifue3f62DmuhKCz2j5CoqHuVBEjiKI1sGxff/ai505wFaCCPDO4Y8TrR3hoSugCfwAAAAfjB8BgkqhkiG9w0BBwagbzBtAgEAMGgGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMfcuTS3R5ZyAF1PTDAgEQgDtb+d24hym8ARlMUAjvypkzjwWCow/vFsOCNNyanBXUpeg1zUS3pm9N2jUdWUkuFthfnIYP/DKha++ntAIAAAAADAAAEACSdsPl9FNdOKFIApY/cT3N2KlcdyRqYpxio+PP/////wAAAAGN+BxTQlHfwz7vgrMAAAAL5Pu3Pkw4G13jdJiZYRHUED00JI226iC/p1xVAGgwZgIxAMk0vt2tIFpTb/YgPsTcvBVF4QYcRu28j8nONHSWLLox2DupiUuUjP5lsFHr15ENRgIxAJxEIV96k5PfFEaCIMvn83NRkXHcT9nphuOQd6FNRy0DeAuWOeApRQuZ4Ti0mVy/aA==
    
    $ DECRYPTED_VALUE=$(kms-encryption decrypt --env "ENCRYPTED_VALUE" --prefix "decrypt:")
    $ echo $DECRYPTED_VALUE
    This is some super secret string
    
    $ echo "{\"value\": \"$ENCRYPTED_VALUE\"}" | kms-encryption decrypt-json --prefix "decrypt:")
    {"value":"This is some super secret string"}
    
## Additional scripts
    
The library also exposes an additional Bash script helpful in automated deployments:

* `decrypt-and-start` - Decrypts all the environment variables that start with `decrypt:` and saves the decrypted values in the same environment variables. Then it executes the passed parameters. This script can be used as an entrypoint in a Dockerfile.

## Troubleshooting

If you fail to install the package with `pip` due to an error in compiling the `cryptography` package, you might need to install additional system dependencies. Instructions below:

### CentOS

    yum install -y gcc libffi-devel python-devel openssl-devel
    
### Debian/Ubuntu

    apt-get install -y build-essential libssl-dev libffi-dev python-dev
    
### MacOS
    
Please make sure you have openssl installed (it should be as a part of system default packages).
