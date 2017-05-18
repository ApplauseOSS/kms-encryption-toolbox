#!/usr/bin/env bash

ENV_VARS=$(env)
for KVP in $ENV_VARS; do
  NAME=$(echo ${KVP} | cut -d '=' -f 1)
  VALUE=$(echo ${KVP} | cut -d '=' -f 2-)
  if [[ "${VALUE}" == decrypt:* ]]; then
    echo "Decrypting the value of ${NAME}..."
    export "${NAME}"=$(applause-encryption decrypt --env "${NAME}" --prefix "decrypt:")
  fi
done

exec "$@"
