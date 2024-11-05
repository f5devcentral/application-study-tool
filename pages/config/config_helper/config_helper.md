---
layout: page
title: Configuration Helper (Recommended)
parent: Configuration
nav_order: 3
has_children: true
permalink: /config/config_helper
---

# Managing AST Collector Configs With Config Helper

This configuration section applies to the AST Opentelemetry Collector. For Grafana, Prometheus or other
components, see the corresponding documentation in [> Components]({{ site.url }}{{ site.baseurl }}/components)

## Background
AST includes a helper python script that can be used to streamline the management of the Opentelemetry
collector. 

At a high level, it merges a set of default configuration  settings with device specific
override settings, and outputs Opentelemetry Collector compatible configuration files that are mounted
by the container at runtime.

{: .important }
The config helper script must run after any changes to the default or device specific configs,
and the otel container restarted before changes will take effect.

## Before You Start
The default settings file reduces the amount of boilerplate that must be configured for each BigIP device
to be monitored.

* [Configuration >	Configuration Helper (Recommended) > Default Configuration]({{ site.url }}{{ site.baseurl }}/config/config_helper/config_defaults.html)

Settings without a logical default (e.g. url of the bigIP device) or wishing to override the default can
be set as described in:

* [Configuration >	Configuration Helper (Recommended) > Device Configuration]({{ site.url }}{{ site.baseurl }}/config/config_helper/config_receivers.html)

## Run The Configuration Helper
The config helper script can be run via docker (or natively if the system has python installed)
from the project root directory as follows:

#### Run With Docker
```bash
# Run the configuration generator from the project root directory
# If `echo $PWD` doesn't give you the current directory on your system,
# replace the '-v ${PWD}' section with '-v /path/to/your/directory'
$ docker run --rm -it -w /app -v ${PWD}:/app --entrypoint /app/src/bin/init_entrypoint.sh python:3.12.6-slim-bookworm --generate-config
```

#### Run With System Python
```bash
$ pip install PyYAML==6.0.2
$ python /app/src/config_helper.py --generate-config
```


## Verify Output
Both of the above commands write 2 new files in the /services/otel_collector directory, which are
the actual files used by the OTEL Collector to configure itself at runtime.

* `receivers.yaml` - The final list of scraper configs and their settings.
* `pipelines.yaml` - The final pipeline configs that map receivers to output destinations
(prometheus).


#### Receivers File
The `/services/otel_collector/receivers.yaml` file contains the OTEL Collector receivers configuration
[/services/otel_collector/receivers.yaml](https://github.com/f5devcentral/application-study-tool/blob/main/services/otel_collector/receivers.yaml)
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

#### Pipelines File
The `/services/otel_collector/pipelines.yaml` file contains the OTEL Collector pipelines configuration
[/services/otel_collector/pipelines.yaml](https://github.com/f5devcentral/application-study-tool/blob/main/services/otel_collector/pipelines.yaml)
which is the merged contents of the default config pipelines section plus the list of receivers 
(bigip scrape jobs):
```yaml
metrics/bigip:
  exporters:
  - otlphttp/metrics-bigip
  - debug/bigip
  processors:
  - batch/local
  receivers:
  # This was inserted here because the `pipeline` for this device
  # or global `default_pipeline` was set to "metrics/bigip"
  - bigip/1
```

2. The second contains the OTEL Collector receivers configuration
[/services/otel_collector/receivers.yaml](https://github.com/f5devcentral/application-study-tool/blob/main/services/otel_collector/receivers.yaml)
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
  username: SOME_OVERRIDE_ACCOUNT_NAME
  tls:
    ca_file: ""
    insecure_skip_verify: false
```

## Restart The AST Containers
Whenever the AST Configuration Files are updated, the containers need to be restarted for the updates
to take effect. This can be accomplished in a few ways, but the simplest is typically:

(From the project root directory)
```bash
$ docker-compose down
$ docker-compose up -d
```