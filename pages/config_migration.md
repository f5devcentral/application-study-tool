# AST Config Migration for Pre v0.6.0 Deployments

## Background
The configuration mangagement for AST Otel Collector is being updated to allow for more flexible 
configuration, and to simplify configuration for advanced usecases.

> Before you start, make sure to backup the /config/big-ips.json file!

The old configuration process relied on a docker container that would run each time the AST
docker-compose instance was started. The process wrote the generated configs to an internal volume
where users were unable to view and modify the files to tune parameters for their deployment.

In the new process, the raw otel configs are exposed in the /services/otel_collector directory where
they can be managed manually, or through continued use of a refactored config_helper script.

For additional detail on configuration management options in the post v0.6.0 scheme, please see [Config Management](https://github.com/f5devcentral/application-study-tool/blob/main/config_management.md)

## Migrating From pre v0.6.0 Configs
There's a python script in /src/config_helper.py which will convert the original big-ips.json schema
into the new management format. Assuming you have an existing list of configured BigIPs in
/config/big-ips.json, migration is a 2 step process:

0. Backup the existing /config/big-ips.json file.
1. Make sure the default values in [/config/ast_defaults.yaml](https://github.com/f5devcentral/application-study-tool/blob/main/config/ast_defaults.yaml) match your
desired default settings.
2. Run the migration script.
3. Run the config generation script.


## Verify Default Settings
The default settings in [/config/ast_defaults.yaml](https://github.com/f5devcentral/application-study-tool/blob/main/config/ast_defaults.yaml) are merged with your existing values in big-ips.json by the script.

You can reduce the amount of repetitive yaml in the output by making sure these values match
your common values (e.g. if you use the username: "telemetry", updating that value in the defaults
file will prevent each per-bigip config stanza from containing that value to overide the "admin"
value).

The script will intelligently merge values that are logically equivalent but not identical.
In particular:

* password_env_ref in big-ips.json will be converted to the password field with the OTEL Collector 
compatible env escaping "\${env:NAME}". Be sure to use the "\${env:BIGIP_PASSWORD_1}" format in the
ast_defaults file.
* collection_interval in big-ips.json was an int - it will be converted to string with the "s" suffix.
* tls_insecure_skip_verify in big-ips.json is converted to the nested tls.insecure_skip_verify setting.
* ca_file in big-ips.json is converted to the nested tls.ca_file setting.

```yaml
# These configs are applied to each entry in the bigip_receivers file
# where they don't contain an equivalent / overriding entry.
bigip_receiver_defaults:
  # The time to wait between metric collection runs
  collection_interval: 60s
  # The username to login to the device with
  username: admin
  # The password (not recommended) or a reference to an env variable (recommended)
  # Below tells the collector to look for an environment variable named BIGIP_PASSWORD_1
  password: "${env:BIGIP_PASSWORD_1}"
  # The data_types that should be enabled or disabled. DNS and GTM users can enable those modules
  # by setting the below to true. These will apply to all devices and may be better specified on the
  # per-reciever settings file below.
  data_types:
    f5.dns:
      enabled: false
    f5.gtm:
      enabled: false
  # The TLS settings to use. Either a CA file must be specified or insecure_skip_verify
  # set to true (not recommended)
  tls:
    insecure_skip_verify: false
    ca_file: ""

# Most people should not need to modify settings below this line
# The default pipeline to use if one isn't specified in the per-device configs.
pipeline_default: metrics/bigip

# These pipeline configs are written to the OTEL config after having the configured receivers
# added to the dictionary in accordance with the "pipeline_default" field above and "pipeline"
# field on the per-receiver config file. Otel Collector documentation explains the syntax in more
# detail.
pipelines:
  metrics/bigip:
    #receivers list are generated via the config helper script
    processors: [batch]
    exporters: [otlphttp/metrics-bigip, debug/bigip]
```

## Run The Conversion Script

The [/src/config_helper.py](https://github.com/f5devcentral/application-study-tool/blob/main/src/config_helper.py) script can be run on a system with python or via docker image as follows:

### Conversion Run Via Docker
If you don't have an environment with python handy, you can run the script via
docker as follows:

```shell
docker run --rm -it -w /app -v ${PWD}:/app --entrypoint /app/src/bin/init_entrypoint.sh python:3.12.6-slim-bookworm --convert-legacy-config --dry-run 
```

You should see output similar to:
```
...
2024-09-25 17:04:46,420 - INFO - Converted the legacy config to the following bigip_receivers.yaml output:

bigip/1:
  endpoint: https://10.0.0.1
bigip/2:
  endpoint: https://10.0.0.2
  password: ${env:BIGIP_PASSWORD_2}
```

If the planned output looks correct, you can run again without the --dry-run to update
the contents of [./config/bigip_receivers.yaml](https://github.com/f5devcentral/application-study-tool/blob/main/config/bigip_receivers.yaml)
```shell
docker run --rm -it -w /app -v ${PWD}:/app --entrypoint /app/src/bin/init_entrypoint.sh python:3.12.6-slim-bookworm --convert-legacy-config
```
Output:
```
...
2024-09-25 17:06:29,897 - INFO - Successfully wrote data to './config/bigip_receivers.yaml'.
```

### Conversion Via System Python

If you have a recent version of python available, you can install dependencies
and run the config helper to view expected from the project root as follows.
```shell
pip install -r requirements.txt
python ./src/config_helper.py --convert-legacy-config --dry-run
```
You should see output similar to:
```
...
2024-09-25 17:04:46,420 - INFO - Converted the legacy config to the following bigip_receivers.yaml output:

bigip/1:
  endpoint: https://10.0.0.1
bigip/2:
  endpoint: https://10.0.0.2
  password: ${env:BIGIP_PASSWORD_2}
```

If the planned output looks correct, you can run again without the --dry-run to update
the contents of [./config/bigip_receivers.yaml](https://github.com/f5devcentral/application-study-tool/blob/main/config/bigip_receivers.yaml)
```shell
python ./src/config_helper.py --convert-legacy-config
```
Output:
```
...
2024-09-25 17:06:29,897 - INFO - Successfully wrote data to './config/bigip_receivers.yaml'.
```

## Run The Configuration Helper To Generate New Configs
The config helper script can be run natively or via docker from the project root directory
to merge the default and device level configs into the final OTEL Collector config as follows:
```shell
# Run the configuration generator from the project root directory
docker run --rm -it -w /app -v ${PWD}:/app --entrypoint /app/src/bin/init_entrypoint.sh python:3.12.6-slim-bookworm --generate-config
```

This will write 2 new files in the services/otel_collector directory:

* `receivers.yaml` - The final list of scraper configs and their settings.
* `pipelines.yaml` - The final pipeline configs that map receievers to output destinations
(prometheus).

### Adding New Devices
To add new devices or update the config after changes to the ast_defaults.yaml or receivers.yaml files,
re-run the config helper script as shown above.