---
layout: page
title: Device Configuration
parent: Configuration Helper (Recommended)
grandparent: Configuration Management
nav_order: 2
---

## Configure Per-Device (BigIP) Settings

The [/config/bigip_receivers.yaml](https://github.com/f5devcentral/application-study-tool/blob/main/config/bigip_receivers.yaml)
file contains settings that are applied to each "BigIP Receiver" (the part that collects data from a
device) within the OTEL Collector config.

{: .important }
The config helper script must run after any changes to the default or device specific configs,
and the otel container restarted before changes will take effect.

The settings in this file are merged with the defaults outlined
in [Configuration >	Configuration Helper (Recommended) > Default Configuration]({{ site.url }}{{ site.baseurl }}/config/config_helper/config_defaults.html), with the more specific settings in this file taking precedence.

The following constraints apply:
* There must be a top level entry for each BigIP Device you wish to monitor.
* The top level key must start with `bigip/`, and be unique (recommend hostname or just incrementing int)
* Each entry must have at minimum the `endpoint` entry containing the url of the device to scrape.

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
