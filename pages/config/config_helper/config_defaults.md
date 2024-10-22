---
layout: page
title: Default Configuration
parent: Configuration Helper (Recommended)
grandparent: Configuration
nav_order: 1
---

## Configure Default Project Settings

1. TOC
{:toc}

The file [/config/ast_defaults.yaml](https://github.com/f5devcentral/application-study-tool/blob/main/config/ast_defaults.yaml)
contains global configuration settings that can be used to reduce the amount of boilerplate configuration
required for each BigIP device to be monitored.

Settings for each device are configured as described in [Configuration >	Configuration Helper (Recommended) > Device Configuration]({{ site.url }}{{ site.baseurl }}config/config_helper/config_receivers.html)

{: .important }
The config helper script must run after any changes to the default or device specific configs,
and the Otel container restarted before changes will take effect.

The config file appears as follows. Syntax for the bigip_receiver_defaults settings follow the spec laid 
out in the [BigIP Receiver Readme]({{ site.url }}{{ site.baseurl }}components/otel_collector/receiver_readme.html) file.

Details for each section are provided below.

```yaml
bigip_receiver_defaults:
  collection_interval: 60s
  username: admin
  password: "${env:BIGIP_PASSWORD_1}"
  data_types:
    f5.dns:
      enabled: false
    f5.gtm:
      enabled: false
  tls:
    insecure_skip_verify: false
    ca_file: ""

f5_data_export: false

# Most people should not need to modify settings below this line
pipeline_default: metrics/local
f5_pipeline_default: metrics/f5-datafabric

pipelines:

  metrics/local:
    #receivers list are generated via the config helper script
    processors: [batch/local]
    exporters: [otlphttp/metrics-local, debug/bigip]

  metrics/f5-datafabric:
    #receivers list are generated via the config helper script
    processors: [interval/f5-datafabric, attributes/f5-datafabric, batch/f5-datafabric]
    exporters: [otlp/f5-datafabric, debug/bigip]
```


### Bigip Receiver Defaults
These configs are applied to each entry in the bigip_receivers file where they don't contain an 
equivalent / overriding entry.

```yaml
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
```

### F5 Data Export Flag
Set to true to enable periodic metric export to F5 DataFabric.
Requires adding your Sensor ID and secret token to the container environment (see .env-example).
Contact your F5 sales rep to obtain the ID / secret token.

```yaml
f5_data_export: false
```

### Pipeline Default Settings
These settings shouldn't need to be changed for most users, but they control the pipeline assignment
for each configured BigIP Receiver. The name of the pipeline_default and/or f5_pipeline_default must
match a configured pipeline from the pipelines settings section below.

The f5_pipeline_default is only applied when the above `f5_data_export` flag is set to true

```yaml
# The default local pipeline to use if one isn't specified in the per-device configs.
pipeline_default: metrics/local
# The default pipeline to use if metric export to F5 is enabled
# (if f5_data_export.sensor_id field above is set)
f5_pipeline_default: metrics/f5-datafabric
```

### Pipelines Configs
These pipeline configs are written to the OTEL config after having the configured receivers
added to the dictionary in accordance with the "pipeline_default" field above and "pipeline"
field on the per-receiver config file. Otel Collector documentation explains the syntax in more
detail.

You can include additional processors or adjust order (but most people shouldn't do this) for any valid
processor type as configured in the base default config file in /services/otel_collector/defaults/ 
directory.

```yaml
pipelines:
  metrics/local:
    #receivers list are generated via the config helper script
    processors: [batch/local]
    exporters: [otlphttp/metrics-local, debug/bigip]

  metrics/f5-datafabric:
    #receivers list are generated via the config helper script
    processors: [interval/f5-datafabric, attributes/f5-datafabric, batch/f5-datafabric]
    exporters: [otlp/f5-datafabric, debug/bigip]
```