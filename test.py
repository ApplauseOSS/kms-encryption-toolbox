import aws_encryption_sdk

kms_key_provider = aws_encryption_sdk.StrictAwsKmsMasterKeyProvider(key_ids=[
   'arn:aws:kms:us-east-1:873559269338:key/1e1a6a81-93e0-4b9a-954b-cc09802bf3ce'
])
my_plaintext = 'This is some super secret data!  Yup, sure is!'

client = aws_encryption_sdk.EncryptionSDKClient(
    commitment_policy=aws_encryption_sdk.CommitmentPolicy.FORBID_ENCRYPT_ALLOW_DECRYPT,
)

my_ciphertext, encryptor_header = client.encrypt(
    source=my_plaintext,
    key_provider=kms_key_provider
)

decrypted_plaintext, decryptor_header = client.decrypt(
    source=my_ciphertext,
    key_provider=kms_key_provider
)

assert my_plaintext == decrypted_plaintext.decode('ascii')
assert encryptor_header.encryption_context == decryptor_header.encryption_context
