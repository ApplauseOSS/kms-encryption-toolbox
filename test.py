import aws_encryption_sdk

kms_key_provider = aws_encryption_sdk.KMSMasterKeyProvider(key_ids=[
   'arn:aws:kms:us-east-1:873559269338:key/1e1a6a81-93e0-4b9a-954b-cc09802bf3ce'
])
my_plaintext = 'This is some super secret data!  Yup, sure is!'

my_ciphertext, encryptor_header = aws_encryption_sdk.encrypt(
    source=my_plaintext,
    key_provider=kms_key_provider
)

decrypted_plaintext, decryptor_header = aws_encryption_sdk.decrypt(
    source=my_ciphertext,
    key_provider=kms_key_provider
)

assert my_plaintext == decrypted_plaintext.decode('ascii')
assert encryptor_header.encryption_context == decryptor_header.encryption_context
