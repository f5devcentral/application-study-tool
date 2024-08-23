#! /usr/bin/env bash

set -e

echo "#===================================================#"
echo "This script will install F5 Application Study Tool"
echo "#===================================================#"
echo "Checking for requirements: docker, git & jq ..."
if ! command -v docker &> /dev/null
then
    echo "docker could not be found"
    exit 1
else
    echo "docker is installed."
fi

if ! command -v git &> /dev/null
then
    echo "git could not be found"
    exit 1
else
    echo "git is installed."
fi

if ! command -v jq &> /dev/null
then
    echo "jq could not be found"
    exit 1
else
    echo "jq is installed."
fi

echo "Checking for repository & registry credentials..."
if [[ -z "${GITLAB_ON_PREM_INSTALL_TOKEN}" ]]; then
    echo "GITLAB_ON_PREM_INSTALL_TOKEN is not set, this environment variable is required."
    exit 1
else
    echo "Found GITLAB_ON_PREM_INSTALL_TOKEN in env"
fi

echo "Login to docker registry..."

echo "$GITLAB_ON_PREM_INSTALL_TOKEN" | docker login registry.gitlab.com -u slc --password-stdin

DOCKER_LOGIN_INFO=`jq '.auths | length' ~/.docker/config.json`
if [ $DOCKER_LOGIN_INFO -eq 0 ]; then
    echo 'docker user could not login. Please verify your GITLAB_ON_PREM_INSTALL_TOKEN is valid'
    exit 1
else
    echo 'docker user logged in'
fi

echo "Cloning repository..."
git clone "https://slc:$GITLAB_ON_PREM_INSTALL_TOKEN@gitlab.com/f5/greenhouse/apps/seven-layer-cake.git" f5-ast

if [ -d ./f5-ast ]
then
    echo "1. Make sure to copy ./f5-ast/.env-example to ./f5-ast/.env"
    echo "2. Make sure to copy ./f5-ast/.env.device-secrets-example to ./f5-ast/.env.device-secrets and edit this (JSON) to establish your BIG-IP's iControlREST passwords"
    echo "3. You must edit ./f5-ast/config/big-ips.json to reflect your BIG-IP fleet's usernames, addresses, etc..."
    echo "You can run F5 Application Study Tool like so:"
    echo "cd ./f5-ast && docker compose up"
    echo "You can update F5 Application Study Tool by running:"
    echo "cd ./f5-ast && git pull"
fi
