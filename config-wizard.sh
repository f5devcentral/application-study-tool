#!/bin/bash

echo
echo "APPLICATION STUDY TOOL CONFIGURATION WIZARD"
echo "Note: This script is meant to be run only at initial installation time. If you need to make changes afterwards or you make an error while inputting the required values, you will need to re-run the script and enter everything all over again. Alternatively, to just make one-off edits, you can manually edit the config files after the script exits."

# THE FOLLOWING STEPS ARE PREREQS FOR THIS SCRIPT:
# (Install Docker)
# git clone https://github.com/f5devcentral/application-study-tool.git
# cd application-study-tool
# chmod +x config-wizard.sh
# Then the user can run this setup wizard by running "./config-wizard.sh".

# Check if .env file, .env.device-secrets, and config directory do not exist. If they don't, but the example files exist, copy the example files to the actual files.
if [ ! -f "./.env" ]; then
  if [ -f "./.env-example" ]; then
    cp .env-example .env
  else # Neither file exists
    echo "Error: neither .env nor .env-example file exists in current directory. Exiting script."
    exit 1
  fi
fi
if [ ! -f "./.env.device-secrets" ]; then
  if [ -f "./.env.device-secrets-example" ]; then
    cp .env.device-secrets-example .env.device-secrets
  else # Neither file exists
    echo "Error: neither .env.device-secrets-example nor .env.device-secrets file exists in current directory. Exiting script."
    exit 1
  fi
fi
if [ ! -d "./config" ]; then
  echo "Error: ./config directory does not exist in current directory. Exiting script."
  exit 1
fi

# Set up some defaults for script:
DEFAULT_USER=admin
DEFAULT_PASS=admin

# SET UP GRAFANA CREDENTIALS
echo "Setting up Grafana dashboard credentials."
echo "Enter desired Grafana username (or press ENTER to leave as default): "
read GF_ADMIN_USER
if [ -n "$GF_ADMIN_USER" ]; then # not empty
  stty -echo
  echo "Enter desired Grafana password (or press ENTER to leave as the default): "
  read GF_ADMIN_PASS
  stty echo
  echo
  GF_ADMIN_PASS="${GF_ADMIN_PASS:-$DEFAULT_PASS}"

  # Update .env file
  sed -i -e s/^GF_SECURITY_ADMIN_USER/#GF_SECURITY_ADMIN_USER/g ./.env
  sed -i -e s/^GF_SECURITY_ADMIN_PASSWORD/#GF_SECURITY_ADMIN_PASSWORD/g ./.env
  echo >> .env
  echo "GF_SECURITY_ADMIN_USER=$GF_ADMIN_USER" >> .env
  echo "GF_SECURITY_ADMIN_PASSWORD=$GF_ADMIN_PASS" >> .env
fi

# TODO: Do the same for SENSOR_ID and SENSOR_SECRET_TOKEN in .env

# CONFIGURE GLOBAL BIG-IP ACCESS
# First, set global default credentials in config/ast_defaults.yaml
echo "Setting up default global BIG-IP credentials."

echo "Enter default global username for BIG-IP (or press ENTER to leave as default: admin): "
read BIGIP_ADMIN_USER
stty -echo
echo "Enter default BIG-IP password (or press ENTER to leave as default): "
read BIGIP_ADMIN_PASS
stty echo
echo

if [ -n "$BIGIP_ADMIN_USER" ]; then # not empty
  # Update config/ast_defaults.yaml
  sed -i -e s/"username\:"/"username\: $BIGIP_ADMIN_USER #"/1 ./config/ast_defaults.yaml
fi

if [ -n "$BIGIP_ADMIN_PASS" ]; then # not empty
  # Update config/ast_defaults.yaml
  sed -i -e s/"password\:"/"password\: $BIGIP_ADMIN_PASS #"/1 ./config/ast_defaults.yaml
fi

# Ask user whether to validate certificates (skip when using self-signed certs)
echo "Skip certificate verification (use self-signed certs) or verify CA certificates (requires CA file name)? "
echo "Enter Y to use self-signed certificates, or N to verify the certificates (or press Enter to leave as default): "
read DONT_VERIFY_CERTS

if [ -n "$DONT_VERIFY_CERTS" ]; then # not empty
  if [[ "$DONT_VERIFY_CERTS" == Y* ]] || [[ "$DONT_VERIFY_CERTS" == y* ]]; then
    # Don't verify certificates
    sed -i -e s/"insecure_skip_verify\:"/"insecure_skip_verify\: true #"/1 ./config/ast_defaults.yaml
    sed -i -e s/"ca_file\:"/"ca_file\: \"\" #"/1 ./config/ast_defaults.yaml
  else
    # Yes, verify certificates
    echo "Enter the full pathname of the CA file: "
    read CA_FILE_PATH
    sed -i -e s/"insecure_skip_verify\:"/"insecure_skip_verify\: false #"/1 ./config/ast_defaults.yaml
    if [ -n "$CA_FILE_PATH" ]; then # not empty
      sed -i -e s~"ca_file\:"~"ca_file\: \"$CA_FILE_PATH\" #"~1 ./config/ast_defaults.yaml
    fi
  fi
fi

# DO WE NEED THIS BLOCK?
# CONFIGURE INDIVIDUAL BIG-IP ACCESS
# Re-check that this file still exists in the current directory
if [ ! -f "./.env.device-secrets" ]; then
  exit 1
fi

echo "Enter the first BIG-IP management IP address (or press Enter to leave unchanged): "
read BIG_IP_ADDR

# Validate IPv4 IP address format
while [[ -n "$BIG_IP_ADDR" ]] && ! [[ "${BIG_IP_ADDR}" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]; do
  echo "Invalid IP address. Enter the first BIG-IP management IPv4 address in a.b.c.d format (or press Enter to stop adding devices): "
  read BIG_IP_ADDR
done;

if [ -n "$BIG_IP_ADDR" ]; then # not empty
  # if file already exists, rename it and create a new file
  if [ -f "./config/bigip_receivers.yaml" ]; then
    mv ./config/bigip_receivers.yaml ./config/bigip_receivers.yaml.old
  fi
  touch ./config/bigip_receivers.yaml
  echo "# Your bigip targets" >> ./config/bigip_receivers.yaml
fi
BIG_IP_NUM=1

while [ -n "$BIG_IP_ADDR" ]; do # while not empty
  echo "CONFIGURING BIG-IP $BIG_IP_NUM ($BIG_IP_ADDR)..."
  echo "Enter this BIG-IP's admin username (press Enter to use global default username and password): "
  read BIGIP_LOCAL_USER
  if [ -n "$BIGIP_LOCAL_USER" ]; then # not empty
    stty -echo
    echo "Enter this BIG-IP's admin password (press Enter to use global default admin password): "
    read BIGIP_LOCAL_PASS
    stty echo
    echo
  fi
  echo "bigip/$BIG_IP_NUM:" >> ./config/bigip_receivers.yaml
  if [[ "$BIG_IP_ADDR" == http* ]]; then
    echo "  endpoint: $BIG_IP_ADDR" >> ./config/bigip_receivers.yaml
  else
    echo "  endpoint: https://$BIG_IP_ADDR" >> ./config/bigip_receivers.yaml
  fi
  if [ -n "$BIGIP_LOCAL_USER" ]; then
    echo "  username: $BIGIP_LOCAL_USER" >> ./config/bigip_receivers.yaml
    if [ -n "$BIGIP_LOCAL_PASS" ]; then
      echo "  password: $BIGIP_LOCAL_PASS" >> ./config/bigip_receivers.yaml
    fi
  fi
  echo "Enter the next BIG-IP management IP address (or press Enter to stop adding devices): "
  read BIG_IP_ADDR

  # Validate IPv4 IP address format
  while [[ -n "$BIG_IP_ADDR" ]] && ! [[ "${BIG_IP_ADDR}" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]; do
    echo "Invalid IP address. Enter the first BIG-IP management IPv4 address in a.b.c.d format (or press Enter to stop adding devices): "
    read BIG_IP_ADDR
  done;

  
  BIG_IP_NUM=$(($BIG_IP_NUM+1))
done

# File configuration is complete. Now prompt the user to run the Configuration Generator container.

# CHECK FOR CONTAINER RUNTIME TOOLS AND PROMPT USER TO RUN THEM.
CONTAINER_RUNTIME="#"
echo "Checking for installation of Docker..."
DOCKER=`command -v docker`
if [ -n "$DOCKER" ]; then # not empty
  echo "Docker is installed."
  CONTAINER_RUNTIME="docker"
else
  PODMAN=`command -v podman`
  if [ -n "$PODMAN" ]; then # not empty
    echo "Podman is installed."
    CONTAINER_RUNTIME="podman"
  else
    echo "Neither Docker nor Podman are installed. Please install one of these tools before continuing."
    exit 1
  fi
fi

# If we got to this point, either Docker or Podman is installed on the sytem.
echo "Would you like to run the configuration generator now (y/n)?"
read RUN_CONFIG_GEN
if [ -n "$RUN_CONFIG_GEN" ]; then # not empty
  if [[ "$RUN_CONFIG_GEN" == Y* ]] || [[ "$RUN_CONFIG_GEN" == y* ]]; then
    # Ask user if sudo is required before docker/podman command
    echo "Do you require 'sudo' to run ${CONTAINER_RUNTIME}? (If you are unsure, choose 'y'.) (y/n)"
    read USER_WANTS_SUDO
    if [[ "$USER_WANTS_SUDO" == Y* ]] || [[ "$USER_WANTS_SUDO" == y* ]]; then
      SUDO_REQUIRED=sudo
    else SUDO_REQUIRED=""
    fi
    # Quick check to see if docker/podman will run successfully.
    $SUDO_REQUIRED $CONTAINER_RUNTIME version > /dev/null
    if ! [[ "$?" == 0 ]]; then
      echo
      echo "$CONTAINER_RUNTIME failed. Check the permissions or try running again with 'sudo'."
      exit 1
    else
    # Initial check passed, so try to run the Config Generator.
      $SUDO_REQUIRED $CONTAINER_RUNTIME run --rm -it -w /app -v ${PWD}:/app --entrypoint /app/src/bin/init_entrypoint.sh python:3.12.6-slim-bookworm --generate-config
      if ! [[ "$?" == 0 ]]; then
        echo
        echo "$CONTAINER_RUNTIME failed. Check the permissions or try running again with 'sudo'."
        exit 1
      fi
    fi
  else
    echo "Configuration files have been created. The next step is to run the configuration generator with the following command (sudo may be required depending on your permissions):"
    echo "  \$ $CONTAINER_RUNTIME run --rm -it -w /app -v ${PWD}:/app --entrypoint /app/src/bin/init_entrypoint.sh python:3.12.6-slim-bookworm --generate-config"
    exit 1
  fi
fi
echo
echo "Configuration complete."
echo

COMPOSE_TOOL="#"
echo "Checking for installation of Docker Compose..."
DOCKER_COMPOSE=`command -v docker-compose`

if [ -n "$DOCKER_COMPOSE" ]; then # not empty
  echo "Docker Compose is installed."
  COMPOSE_TOOL="docker-compose"
else # Docker Compose is not installed. Let's check Podman Compose.
  PODMAN_COMPOSE=`command -v podman-compose`
  if [ -n "$PODMAN_COMPOSE" ]; then # not empty
    echo "Podman is installed."
    COMPOSE_TOOL="podman-compose"
  else # neither is installed
    echo "Neither Docker Compose nor Podman Compose are installed. Please install one of these tools in order to start the service."
    echo "Then run '$SUDO_REQUIRED $COMPOSE_TOOL up'"
    exit 1
  fi
fi

# If we got to this point, either Docker Compose or Podman Compose is installed on the sytem.
echo "Would you like to start the sevice now (y/n)?"
read RUN_SERVICE
if [ -n "$RUN_SERVICE" ]; then # not empty
  if [[ "$RUN_SERVICE" == Y* ]] || [[ "$RUN_SERVICE" == y* ]]; then
    # Quick check to ensure docker-compose file is present
    if [ -f "./docker-compose.yaml" ]; then
      # docker-compose up
      $SUDO_REQUIRED $COMPOSE_TOOL up
      if ! [[ "$?" == 0 ]]; then
        echo
        echo "$COMPOSE_TOOL failed. Check the permissions or try running again with 'sudo'."
        exit 1
      fi
    else
      echo "Error: docker-compose.yaml file does not exist in current directory. Cannot start docker compose service."
      exit 1
    fi
  else
    echo "Configuration is complete. The next step is to run the compose tool to start the service, using the following command:"
    echo "  \$ $SUDO_REQUIRED $COMPOSE_TOOL up"
  fi
else
  echo "Configuration is complete. The next step is to run the compose tool to start the service, using the following command:"
  echo "  \$ $SUDO_REQUIRED $COMPOSE_TOOL up"
fi
