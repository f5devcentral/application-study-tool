# AST Configuration Management Detail

## Config Management Options
In the post v0.6.0 management scheme, users can choose from one of the below options to manage
the AST Otel Collector configs:

1. Using the [/src/config_helper.py](/src/config_helper.py) script to generate full Otel Collector
Config files from a small set of configuration for each device plus a set of defaults (recommended for
most users, and includes migration path from old big-ips.json configs)

2. Manual maintenance of the Otel Collector Config files in
[/services/otel_collector/pipelines.yaml](/services/otel_collector/pipelines.yaml)
and [/services/otel_collector/receivers.yaml](/services/otel_collector/receivers.yaml)

3. Manual maintenance of the Otel Collector Config files in
[/services/otel_collector/defaults](/services/otel_collector/defaults)

### Using config_helper.py (Recommended For Most Users)
With the included python script in [/src/config_helper.py](/src/config_helper.py), AST collector
configuration is managed through 2 primary files:

1. A default file which contains settings that should be applied for each BigIP unless overriden (see below)
in [/config/ast_defaults.yaml](/config/ast_defaults.yaml):

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


# Set to true to enable periodic metric export to F5 DataFabric.
# Requires adding your Sensor ID and secret token to the container environment (see .env-example).
# Contact your F5 sales rep to obtain the ID / secret token.
f5_data_export: false


# Most people should not need to modify settings below this line

# The default local pipeline to use if one isn't specified in the per-device configs.
pipeline_default: metrics/local
# The default pipeline to use if metric export to F5 is enabled (if f5_data_export.sensor_id field above is set)
f5_pipeline_default: metrics/f5-datafabric

pipelines:

  # These pipeline configs are written to the OTEL config after having the configured receivers
  # added to the dictionary in accordance with the "pipeline_default" field above and "pipeline"
  # field on the per-receiver config file. Otel Collector documentation explains the syntax in more
  # detail.
  metrics/local:
    #receivers list are generated via the config helper script
    processors: [batch]
    exporters: [otlphttp/metrics-local, debug/bigip]

  # These pipeline configs are written to the OTEL config after having the configured receivers
  # added to the dictionary in accordance with the "f5_pipeline_default" field above and "f5_pipeline"
  # field on the per-receiver config file. Otel Collector documentation explains the syntax in more
  # detail.
  metrics/f5-datafabric:
    #receivers list are generated via the config helper script
    processors: [batch, interval/f5-datafabric, attributes/f5-datafabric]
    exporters: [otlp/f5-datafabric, debug/bigip]
```

2. A file which contains settings that should override (or have no default) at the individual bigip level
in [/config/bigip_receivers.yaml](/config/bigip_receivers.yaml):
```yaml
# This file contains the list of BigIP receivers (scrape jobs).
# Each item must have a unique key (e.g. bigip/1, bigip/2, etc).
# Values not explicitly configured here inherit values in ast_defaults.yaml.
bigip/1:
  # Endpoint must be specified for each device because there's no rational default.
  endpoint: https://10.0.0.1
  ## Pipeline is used to tell the config_helper script which pipeline to attach it to.
  ## Most users shouldn't configure this (and it will inherit from the value in ast_defaults.yaml)
  # pipeline: metrics/bigip
  ## Anything below here could be uncommented to override the default value
  # collection_interval: 30s
  username: SOME_OVERRIDE_ACCOUNT_NAME
  password: "${SOME_OTHER_ENV_VAR_WITH_ANOTHER_PASSWORD}"
  # data_types:
  #   f5.dns:
  #     enabled: false
  #   f5.gtm:
  #     enabled: false
  # tls:
  #   insecure_skip_verify: false
  #   ca_file: 
```

When the config_helper script is run with the --generate-configs option, 2 new files are written out
to the [/services/otel_collector](/services/otel_collector) directory:

1. The first contains the OTEL Collector pipelines configuration [/services/otel_collector/pipelines.yaml](/services/otel_collector/pipelines.yaml) which is basically the contents of the default config pipelines section plus the list of receivers (bigip scrape jobs):
```yaml
metrics/bigip:
  exporters:
  - otlphttp/metrics-bigip
  - debug/bigip
  processors:
  - batch
  receivers:
  # This was inserted here because the pipeline / default_pipeline for this device was
  # set to "metrics/bigip"
  - bigip/1
```

2. The second contains the OTEL Collector receivers configuration
[/services/otel_collector/receivers.yaml](/services/otel_collector/receivers.yaml)
which is the merged contents of the default config settings and the per-device settings:
```yaml
bigip/1:
  collection_interval: 30s
  data_types:
    f5.dns:
      enabled: false
    f5.gtm:
      enabled: false
  endpoint: https://10.0.0.1
  password: ${SOME_OTHER_ENV_VAR_WITH_ANOTHER_PASSWORD}
  tls:
    ca_file: ""
    insecure_skip_verify: false
  username: SOME_OVERRIDE_ACCOUNT_NAME
```

When the OTEL container is run, the default configs in
[/services/otel_collector/defaults/](/services/otel_collector/defaults/) merge these files into
the final configuration the OTEL Collector needs to run correctly.

### Manual Maintenance Of Receiver and Pipeline Files
The files mentioned above can be managed directly by users if they want to skip the config_helper
script in favor of their own automation / templating. In this case, you just need to update the files:

* [/services/otel_collector/receivers.yaml](/services/otel_collector/receivers.yaml)
* [/services/otel_collector/pipelines.yaml](/services/otel_collector/pipelines.yaml)

These are mapped into the final OTEL Collector config via the "file" directives in the
receivers and services.pipelines section of the
[/services/otel_collector/defaults/bigip-scraper-config.yaml]() file:

```
receivers: ${file:/etc/otel-collector-config/receivers.yaml}

processors:
  batch:

exporters:
  otlphttp/metrics-bigip:
    endpoint: http://prometheus:9090/api/v1/otlp
  debug/bigip:
    verbosity: basic
    sampling_initial: 5
    sampling_thereafter: 200

service:
  pipelines: ${file:/etc/otel-collector-config/pipelines.yaml}

```

Any of these files can be modified directly to update settings as desired (e.g. adding additional
logging levels).


### Manual Maintenance Of The OTEL Collector Config
You can also forgo all of the above config structure in favor of your own management scheme. If you're
running with the base docker-compose file, you may need to modify the commands section to point at your
own config files:

```yaml
  otel-collector:
    ...
    # Update these as needed
    volumes:
      - ./services/otel_collector:/etc/otel-collector-config
    # Update these as needed
    command: 
      - "--config=/etc/otel-collector-config/defaults/default-config.yaml"
      - "--config=/etc/otel-collector-config/defaults/bigip-scraper-config.yaml"
    ...
```