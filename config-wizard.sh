#!/bin/sh

# This setting will cause this script to exit if any errors are encountered.
set -e

echo
echo "APPLICATION STUDY TOOL CONFIGURATION WIZARD"
echo

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
echo "Enter Y to use self-signed certificates, N to verify the certificates (or press Enter to leave as default): "
read SKIP_CERT_VERIFY

if [ -n "$SKIP_CERT_VERIFY" ]; then # not empty
  if [[ "$SKIP_CERT_VERIFY" == Y* || "$SKIP_CERT_VERIFY" == y* ]]; then
    # Don't verify certificates
    sed -i -e s/"insecure_skip_verify\:"/"insecure_skip_verify\: true #"/1 ./config/ast_defaults.yaml
    sed -i -e s/"ca_file\:"/"ca_file\: \"\" #"/1 ./config/ast_defaults.yaml
  else
    # Verify certificates
    echo "Enter the full pathname of the CA file: "
    read CA_FILE_PATH
    sed -i -e s/"insecure_skip_verify\:"/"insecure_skip_verify\: false #"/1 ./config/ast_defaults.yaml
    if [ -n "$CA_FILE_PATH" ]; then # not empty
      sed -i -e s~"ca_file\:"~"ca_file\: \"$CA_FILE_PATH\" #"~1 ./config/ast_defaults.yaml
    fi
  fi
fi

# CONFIGURE INDIVIDUAL BIG-IP ACCESS
# Re-check that this file still exists in the current directory
if [ ! -f "./.env.device-secrets" ]; then
  exit 1
fi

echo "Enter the first BIG-IP management IP address (or press Enter to leave unchanged): "
read BIG_IP_ADDR
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
  BIG_IP_NUM=$(($BIG_IP_NUM+1))
done

echo "Would you like to run the configuration generator now (y/n)?"
read RUN_CONFIG_GEN
if [ -n "$RUN_CONFIG_GEN" ]; then # not empty
  if [[ "$RUN_CONFIG_GEN" == Y* || "$RUN_CONFIG_GEN" == y* ]]; then
    docker run --rm -it -w /app -v ${PWD}:/app --entrypoint /app/src/bin/init_entrypoint.sh python:3.12.6-slim-bookworm --generate-config
  fi
fi
echo
echo "Configuration complete."
echo

echo "Would you like to start the sevice now (y/n)?"
read RUN_SERVICE
if [ -n "$RUN_SERVICE" ]; then # not empty
  if [[ "$RUN_SERVICE" == Y* || "$RUN_SERVICE" == y* ]]; then
    # Quick check to ensure docker-compose file is present
    if [ -f "./docker-compose.yaml" ]; then
      docker compose up
    else
      echo "Error: docker-compose.yaml file does not exist in current directory. Cannot start docker compose service."
      exit 1
    fi
  fi
fi
