# Application Study Tool

## Overview

> Prior to installation, please see the [AST Docsite](https://f5devcentral.github.io/application-study-tool/) for detailed
configuration, troubleshooting (REST changes, HIGH CPU on control plane) info, etc.

> See the [F5 Application Study Tool Labs](https://clouddocs.f5.com/training/community/ast/html/) for an educational guided lab experience.
> 
> For enabling HTTPS within Grafana, see the [Make Grafana Listen on HTTPS guide](https://community.f5.com/kb/technicalarticles/application-study-tool-make-grafana-listen-on-https/341728) for guidance.
>
> To review ideas on integrating your secrets with a vault, see the [Integrating your secrets with Hashi vault](https://community.f5.com/kb/TechnicalArticles/f5-app-study-tool-with-passwords-stored-in-vault/341155) for further information.

The Application Study Tool is intended to provide enhanced insights into (classic) BIG-IP products, leveraging best in class
open source telemetry tools. The full installation includes:

* Custom Instance of OpenTelemetry Collector with enhanced BIG-IP data receivers (data fetched via iControlRest) [Full List of Metrics Collected](pages/components/otel_collector/receiver_metrics.md).
* Prometheus timeseries database for storing and querying collected data.
* Grafana Instance with pre-configured dashboards for quick insights at the device and "fleet" levels.

The Application Study Tool has everything needed to quickly get up and running with application insights at less than
production levels of reliability. For production/operational use cases, you can build on the included components,
accounting for things like high availability, enhanced security via e.g. Grafana OIDC integration, and similar. Alternatively,
the Opentelemetry Collector can be configured to send data to existing production ops monitoring tools as desired.

![](./pages/assets/ui.gif)

## Getting Started

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
vi ./config/bigip_receivers.yaml
# Run the configuration generator
docker run --rm -it -w /app -v ${PWD}:/app --entrypoint /app/src/bin/init_entrypoint.sh python:3.12.6-slim-bookworm --generate-config
# Start the tool (use `docker compose up -d` to start in background mode)
docker compose up
```

## Configuration

For additional configuration management background, see
[AST Configuration Management Overview](https://f5devcentral.github.io/application-study-tool/config).
The below assumes you're using the config_helper script for assisted management.


Application Study Tool config management relies on default configs in
[/configs/ast_defaults.yaml](/config/ast_defaults.yaml) and device specific information in
[/configs/bigip_receivers.yaml](/config/bigip_receivers.yaml).

Settings in the bigip_receivers.yaml override those in ast_defaults.yaml.


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
  # These are disabled by default and users can enable those modules
  # on all devices by setting the below to true.
  # A full list of data_types is at https://f5devcentral.github.io/application-study-tool/components/otel_collector/receiver_readme.html.
  data_types:
    f5.apm:
      enabled: false
    f5.cgnat:
      enabled: false
    f5.dns:
      enabled: false
    f5.dos:
      enabled: false
    f5.firewall:
      enabled: false
    f5.gtm:
      enabled: false
    f5.policy.api_protection:
      enabled: false
    f5.policy.asm:
      enabled: false
    f5.policy.firewall:
      enabled: false
    f5.policy.ip_intelligence:
      enabled: false
    f5.policy.nat:
      enabled: false
    f5.profile.dos:
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
value for the devices that use this password in config/ast_defaults.yaml or device specific
config in config/bigip_receivers.yaml. In the following example, bigip/1 uses BIGIP_PASSWORD_1
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


## Configure Periodic Metric Data Export To F5
The application study tool can be configured to periodically (every 5 minutes) export a snapshot of your
BigIP metrics to F5. Contact your F5 Sales Representative for a "Sensor ID" (a unique string used to associate
your metrics with your Organization) and a "Sensor Secret Token" (used to authenticate to the F5 Datafabric as
an authorized data sender for your Org).

This functionality is enabled as follows:

1. Enable the flag in [config/ast_defaults.yaml](config/ast_defaults.yaml) file as follows:

```yaml
# Set this true to enable periodic metric export to F5 DataFabric.
# Requires adding your sensor ID and secret token to the container environment (see .env-example).
# Contact your F5 sales rep to obtain the ID / secret token.
f5_data_export: true
```

2. Add the Sensor ID and Secret Token to the .env file, or otherwise attach it to the Opentelemetry Collector container
as SENSOR_ID and SENSOR_SECRET_TOKEN (see [.env-example](./.env-example) for example).

3. Run the configuration helper script (see below).

## Run The Configuration Helper
The config helper script can be run natively or via docker to merge the default and device
level configs into the final OTEL Collector config from the project root directory as follows:

**Run With Docker**
```bash
# Run the configuration generator from the project root directory
# If `echo $PWD` doesn't give you the current directory on your system,
# replace the '-v ${PWD}' section with '-v /path/to/your/directory'
$ docker run --rm -it -w /app -v ${PWD}:/app --entrypoint /app/src/bin/init_entrypoint.sh python:3.12.6-slim-bookworm --generate-config
```

**Run With System Python**

This command requires Python to already be installed on the host. If it is not, installation instructions can be found here:
* [Install on Ubuntu](https://docs.python-guide.org/starting/install3/linux/)
* [Install on RHEL and compatible Linux distributions](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/installing_and_using_dynamic_programming_languages/assembly_installing-and-using-python_installing-and-using-dynamic-programming-languages)

```bash
# Run the configuration generator from the project root directory
$ python3 src/config_helper.py --generate-config
```

This will write 2 new files in the services/otel_collector directory:

* `receivers.yaml` - The final list of scraper configs and their settings.
* `pipelines.yaml` - The final pipeline configs that map receivers to output destinations
(prometheus, and optionally F5).

## Adding New Devices or Updating Configs
To add new devices or update the config after changes to the ast_defaults.yaml or receivers.yaml files,
re-run the config helper script as shown above and then restart the otel collector container.

## Account Permissions
The vast majority of telemetry data can be collected with read-only access to the BigIP. Some
granular stats are only available as output to a iControl Rest 'bash' shell command, and
these require read-write access.

If a read-only account is used, the following metrics are unavailable:

```
f5_virtual_server_profile_client_ssl_connection_count{}
f5_virtual_server_profile_client_ssl_bytes_out_total{}
f5_virtual_server_profile_http_responses_total{}
f5_virtual_server_profile_http_requests_total{}
f5_virtual_server_profile_client_ssl_records_out_total{}
f5_plane_cpu_count{}
f5_virtual_server_profile_client_ssl_insecure_handshake_rejects_total{}
f5_virtual_server_profile_client_ssl_premature_disconnects_total{}
f5_virtual_server_profile_client_ssl_renegotiations_total{}
f5_virtual_server_profile_client_ssl_connection_max{}
f5_virtual_server_profile_client_ssl_insecure_handshake_accepts_total{}
f5_virtual_server_profile_client_ssl_bytes_in_total{}
f5_virtual_server_profile_client_ssl_handshake_count{}
f5_virtual_server_profile_client_ssl_records_in_total{}
f5_virtual_server_profile_client_ssl_connection_total{}
f5_policy_ip_intelligence_feed_list_count{}
f5_policy_ip_intelligence_info{}
f5_virtual_server_profile_client_ssl_secure_handshakes_total{}
f5_policy_ip_intelligence_generation{}
f5_pool_member_bytes_in_total{}
f5_pool_member_bytes_out_total{}
f5_pool_member_connection_count{}
f5_pool_member_connections_total{}
f5_pool_member_requests_total{}
f5_pool_member_session_count{}
f5_pool_member_packets_in_total{}
f5_pool_member_packets_out_total{}
f5_plane_cpu_utilization_5s{}
```

This will impact data output in several dashboards/panels (denoted with description fields indicating as such).

You can disable attempts to collect bash information with `enable_bash_collection: false` at the appropriate level (global or device).

```yaml
bigip/1:
  endpoint: https://10.0.0.1
  enable_bash_collection: false
  #...
```

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

```shell
# `docker compose up -d` to start in background mode
docker compose up
```

#### View The Dashboards
The default Grafana user/pass is `admin/admin`, and can be accessed at
`http://<hostname>:3000`.


## Updating AST Versions
Updating to a new release of the AST repo can be done with the following general process:

1. Review the release notes for all intermediate versions and check for warnings about
special instructions / breaking changes.
2. Backup your ast_defaults.yaml and bigip_receivers.yaml files.
3. Stash changes, update the repo state, and unstash changes as follows:
```shell
git stash
git fetch --tags
git pull origin main
git checkout tags/RELEASE_VERSION #(e.g. tags/v0.9.4)
git stash pop
# <merge any conflicts with your local changes>
# <re-run config scripts>
docker compose down
# `docker compose up -d` to start in background mode
docker compose up
```

## Support

For support, please open a GitHub issue.  Note, the code in this repository is community supported and is not supported by F5 Networks.  For a complete list of supported projects please reference [SUPPORT.md](SUPPORT.md).

## Community Code of Conduct

Please refer to the [F5 DevCentral Community Code of Conduct](code_of_conduct.md).

## License

[Apache License 2.0](LICENSE)

## Copyright

Copyright 2014-2024 F5 Networks Inc.

### F5 Networks Contributor License Agreement

Before you start contributing to any project sponsored by F5 Networks, Inc. (F5) on GitHub, you will need to sign a Contributor License Agreement (CLA).

If you are signing as an individual, we recommend that you talk to your employer (if applicable) before signing the CLA since some employment agreements may have restrictions on your contributions to other projects.
Otherwise by submitting a CLA you represent that you are legally entitled to grant the licenses recited therein.

If your employer has rights to intellectual property that you create, such as your contributions, you represent that you have received permission to make contributions on behalf of that employer, that your employer has waived such rights for your contributions, or that your employer has executed a separate CLA with F5.

If you are signing on behalf of a company, you represent that you are legally entitled to grant the license recited therein.
You represent further that each employee of the entity that submits contributions is authorized to submit such contributions on behalf of the entity pursuant to the CLA.
