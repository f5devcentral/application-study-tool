# Application Study Tool

## Overview

The Application Study Tool is intended to provide enhanced insights into (classic) BIG-IP products, leveraging best in class
open source telemetry tools. The full installation inculdes:

* Custom Instance of OpenTelemetry Collector with enhanced BIG-IP data receivers (data fetched via iControlRest).
* Prometheus timeseries database for storing and querying collected data.
* Grafana Instance with pre-configured dashboards for quick insights at the device and "fleet" levels.

The Application Study Tool has everything needed to quickly get up and running with application insights at less than
production levels of reliability. For production/operational use cases, you can build on the included components,
accounting for things like high availability, enhanced security via e.g. grafana OIDC integrationm, and similar. Alternatively,
the openetlemetry collector can be configured to send data to existing production ops monitoring tools as desired.

## Getting Started

### Prerequisites

docker (or compatible) - [Installation Instructions](https://docs.docker.com/engine/install/)

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
# Edit the config file with device / connection info (see "Configure Devices To Scrape" below)
vi ./config/big-ips.json
# Start the tool
docker-compose up
```

### Configure Devices To Scrape
Application Study Tool includes an init container which builds an OpenTelemetry
Collector Configuration file based on a provided list of BIG-IPs in JSON format.

Edit config/big-ips.json to reflect your list of BIG-IPs and their access credentials:
```json
[
  {
    // Set this to the management IP for the device. This must be
    // reachable from the Application Study Tool host.
    "endpoint": "https://10.0.0.1",
    // Set this to the desired account's user name
    "username": "admin",
    // This field tells the collector the name of an environment variable
    // which contains the password for the device.
    // This field does not contain the password itself.
    "password_env_ref": "BIGIP_PASSWORD_1",
    // Secure TLS communication requires mounting the certificate bundle
    // used to sign the BigIP certificates. Though not recommended, in the
    // case of self-signed certificates or for testing purposes, you can skip
    // this check by setting this field to true.
    "tls_insecure_skip_verify": false,
    // The path to a CA File used to validate BIG-IP certificates. This is required
    // if tls_insecure_skip_verify is set to false. See below for details.
    "ca_file": "",
  }
]
```

### Configure Device Secrets
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
value for the devices that use this password in config/big-ips.json.

#### Account Permissions
The vast majority of telemetry data can be collected with read-only access to the BigIP. Some
granular stats are only available as output to a iControl Rest 'bash' shell command, and these require
read-write access. If a read-only account is used, the following metrics are unavailable:

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
f5_plane_cpu_utilization_5s{}
```

This will impact data output in several dashboards/panels (denoted with description fields indicating as such).

### Configure CA File
AST expects a valid TLS cert bundle unless `tls_insecure_skip_verify` is
set to true for each device. In order to mount and use your CA file, you must
configure the docker-compose.yaml file in this directory, and set the `ca_file` parameter to the resulting path. Example:

docker-compose.yaml:
```yaml
  ...
  otel-collector:
    ...
    volumes:
      - otel_collector:/etc/otel-collector-config
      - ./config/ca_bundle.pem:/etc/ssl/ca_bundle.pem
```

big-ips.json:
```json
[
  { // device 1
    ...
    "ca_file": "/etc/ssl/ca_bundle.pem",
  },
  { // device 2
    ...
    "ca_file": "/etc/ssl/ca_bundle.pem",
  },
]
```

The configuration paramteter `tls_insecure_skip_verify` defaults to false. Installers
 that would like to opt-in to run in an insecure TLS mode must set
 `tls_insecure_skip_verify: true` for each BIG-IP in the config array and understand
 that the connection between the OTEL collector and the BIG-IP does not have secure
 TLS termination.

### Configure Grafana
The Grafana instance can be configured via environment variable using their standard
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
The default grafana user/pass is `admin/admin`, and can be accessed at
`http://<hostname>:3000`.


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
