#!/usr/bin/env bash

mkdir -p ~/.aws

cat > ~/.aws/credentials << EOF
[default]
aws_secret_access_key=${aws_secret_access_key}
aws_access_key_id=${aws_access_key_id}
EOF
