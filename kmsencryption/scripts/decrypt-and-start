#!/usr/bin/env bash

set -e

ENV_VARS=$(env)
for KVP in $ENV_VARS; do
  NAME=$(echo ${KVP} | cut -d '=' -f 1)
  VALUE=$(echo ${KVP} | cut -d '=' -f 2-)
  if [[ "${VALUE}" == decrypt:* ]]; then
    echo "Decrypting the value of ${NAME}..."
    export "${NAME}"=$(kms-encryption decrypt --env "${NAME}" --prefix "decrypt:")
  fi
done

exec "$@"
