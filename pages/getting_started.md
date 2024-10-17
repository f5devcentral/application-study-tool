---
layout: page
title: Getting Started
nav_order: 2
---
# Getting Started

1. TOC
{:toc}

## Background
This instructions in this file will get a new installation up and running in as little as a few minutes.
For more detailed information on AST config management options, see the
[Configuration Management Overview]({{site.baseurl}}/config/) and related sections.

### Prerequisites

[Git Client](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

Docker (or compatible) container environment with compose.

Installation Instructions:
  * [General (docker engine)](https://docs.docker.com/engine/install/)
  * [Ubuntu (docker engine)](https://docs.docker.com/engine/install/ubuntu/)
  * [RHEL (docker engine)](https://docs.docker.com/engine/install/rhel/)
  * [Podman](https://podman.io/docs/installation)

### Installation

Clone the repo or download source tarball from the [release](https://github.com/f5devcentral/application-study-tool/releases) section.

```shell
# Clone the repo
git clone https://github.com/f5devcentral/application-study-tool.git
cd application-study-tool
# Edit the following file with Grafana variables as required
cp .env-example .env
# Edit the following file with device secrets as required (see "Configure Device Secrets" below)
cp .env.device-secrets-example .env.device-secrets
# Edit the default settings for your environment as required
# (see "Configure Default Device Settings" below)
vi ./config/ast_defaults.yaml
# Edit the config file with device / connection info
# (see "Configure Devices To Scrape" below)
vi ./config/big_receivers.yaml
# Run the configuration generator
docker run --rm -it -w /app -v ${PWD}:/app --entrypoint /app/src/bin/init_entrypoint.sh python:3.12.6-slim-bookworm --generate-config
# Start the tool
docker-compose up
```

## Configure Default Device Settings

Edit config/ast_defaults.yaml to reflect common values for your BIG-IPs:
```yaml
# These configs are applied to each entry in the bigip_receivers file
# where they don't contain an equivalent / overriding entry.
bigip_receiver_defaults:
  # The time to wait between metric collection runs
  collection_interval: 60s
  # The username to login to the device with
  username: admin
  # The password (not recommended) or a reference to an env variable (recommended)
  # Below tells the collector to look for an environment variable named
  # BIGIP_PASSWORD_1
  password: "${env:BIGIP_PASSWORD_1}"
  # The data_types that should be enabled or disabled.
  # DNS and GTM are disabled by default and users can enable those modules
  # on all devices by setting the below to true.
  # A full list of data_types is in /docs/receiver_readme.md.
  data_types:
    f5.dns:
      enabled: false
    f5.gtm:
      enabled: false
  # The TLS settings to use. Either a CA file must be specified or
  # insecure_skip_verify set to true (not recommended).
  tls:
    # Secure TLS communication requires mounting the certificate bundle
    # used to sign the BigIP certificates. Though not recommended, in the
    # case of self-signed certificates or for testing purposes, you can skip
    # this check by setting this field to true.
    insecure_skip_verify: false
    # The path to a CA File used to validate BIG-IP certificates. This is required
    # if tls_insecure_skip_verify is set to false. See below for details.
    ca_file: ""
```

## Configure Devices To Scrape
Edit the device list in config/bigip_receivers.yaml:
```yaml
#### Values not explicitly configured here inherit values in ast_defaults.yaml.
#### Each entry must have a unique name, starting with bigip/ 
#### (e.g. bigip/1, bigip/2)
bigip/1:
  #### Endpoint must be specified for each device
  #### because there's no rational default.
  #### Set this to the management IP for the device. This must be
  #### reachable from the Application Study Tool host.
  endpoint: https://10.0.0.1
  #### Override some default settings with device specific values
  username: SOME_OVERRIDE_ACCOUNT_NAME
  password: "${SOME_OTHER_ENV_VAR_WITH_ANOTHER_PASSWORD}"
  #### Everything commented out here gets the value from default
  # collection_interval: 30s
  # data_types:
  #   f5.dns:
  #     enabled: false
  #   f5.gtm:
  #     enabled: false
  # tls:
  #   insecure_skip_verify: true
  #   ca_file:
bigip/2:
  endpoint: https://10.0.0.2
```


## Configure Device Secrets
The application study tool default configuration relies on environment variables
which contain device access credentials. There are a number of ways to manage and
inject secrets into a container environment (modifications to the docker-compose file
to support your preferred management process are encouraged), but for simplicity,
if there is a file named .env.device-secrets in the root project directory they will be
mounted.

Create a file called .env.device-secrets, and add your BIP passwords like so:
```
BIGIP_PASSWORD_1=foo-bar123!
BIGIP_PASSWORD_2=bar-foo123!
```

The variable name (the part on the left of the equal sign) must match the configured
value for the devices that use this password in config/ast_defaults.yaml or device specifc
cofig in config/bigip_receivers.yaml. In the following example, bigip/1 uses BIGIP_PASSWORD_1
from  the defaults and bigip/2 uses BIGIP_PASSWORD_2 from the device settings:

```
##############################
## config/ast_defaults.yaml 
##############################

bigip_receiver_defaults:
  ...
  password: "${env:BIGIP_PASSWORD_1}"
  ...

##############################
## config/bigip_receivers.yaml
##############################

# This gets the default "${env:BIGIP_PASSWORD_1}"
bigip/1:
  endpoint: https://10.0.0.1

# This overrides it with "${env:BIGIP_PASSWORD_2}"
bigip/2:
  endpoint: https://10.0.0.1
  password: ${env:BIGIP_PASSWORD_2}

```

## Run The Configuration Helper
The config helper script can be run natively or via docker from the project root directory
to merge the default and device level configs into the final OTEL Collector config as follows:
```shell
# Run the configuration generator from the project root directory
# If `echo $PWD` doesn't give you the current directory on your system,
# replace the '-v ${PWD}' section with '-v /path/to/your/directory'
docker run --rm -it -w /app -v ${PWD}:/app --entrypoint /app/src/bin/init_entrypoint.sh python:3.12.6-slim-bookworm --generate-config
```

This will write 2 new files in the services/otel_collector directory:

* `receivers.yaml` - The final list of scraper configs and their settings.
* `pipelines.yaml` - The final pipeline configs that map receievers to output destinations
(prometheus).

### Configure CA File
AST expects a valid TLS cert bundle unless `tls.insecure_skip_verify` is
set to true for each device. In order to mount and use your CA file, you must
configure the docker-compose.yaml file in this directory, and set the `ca_file` parameter to
the resulting path. Example:

docker-compose.yaml:
```yaml
  ...
  otel-collector:
    ...
    volumes:
      - ./services/otel_collector:/etc/otel-collector-config
      - ./config/ca_bundle.pem:/etc/ssl/ca_bundle.pem
```

config/ast_defaults.yaml (or the tls section of each device in config/bigip_receivers.yaml):
```yaml
bigip_receiver_defaults:
  ...
  tls:
    insecure_skip_verify: false
    ca_file: "/etc/ssl/ca_bundle.pem"
```

The configuration parameter `tls.insecure_skip_verify` defaults to false. Installers
who would like to opt-in to run in an insecure TLS mode must set
`tls.insecure_skip_verify: true` and understand
that the connection between the OTEL collector and the BIG-IP does not have secure
TLS termination.

### Configure Grafana
The Grafana instance can be configured via environment variables using their standard
[options](https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/#override-configuration-with-environment-variables).

The included .env-example can be copied over and modified to set the initial admin
password to a value you select:

```
cp .env-example .env
<edit .env with desired admin password and any other variables>
```

### Run Application Study Tool
Once the above configurations have been made, the tool can be started with:

```
docker compose up
```

#### View The Dashboards
The default Grafana user/pass is `admin/admin`, and can be accessed at
`http://<hostname>:3000`.
