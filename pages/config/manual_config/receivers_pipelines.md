---
layout: page
title: Receiver/Pipeline Config
parent: Manual Configuration
grandparent: Configuration
nav_order: 1
---

## Manual Configuration With The Receivers and Pipelines Files


1. TOC
{:toc}

As described in the Config Helper section, the output of the helper is 2 yaml files that are used by
the Otel Collector at run time. 

* `receivers.yaml` - The final list of scraper configs and their settings.
* `pipelines.yaml` - The final pipeline configs that map receievers to output destinations
(prometheus).


{: .important }
The OTEL Collector Container must be restarted before changes to these files will take effect.

These files can be modified directly by users without the config helper script without any additional
changes to the AST docker-compose or other settings.

Syntax for these files is the [Opentelemetry Collector Configuration](https://opentelemetry.io/docs/collector/configuration/) syntax.

#### Receivers File
The `/services/otel_collector/receivers.yaml` file contains the OTEL Collector receivers configuration:
```yaml
bigip/1:
  collection_interval: 30s
  data_types:
    f5.dns:
      enabled: false
    f5.gtm:
      enabled: false
  endpoint: https://10.0.0.1
  password: ${env:SOME_OTHER_ENV_VAR_WITH_ANOTHER_PASSWORD}
  tls:
    ca_file: ""
    insecure_skip_verify: false
  username: SOME_OVERRIDE_ACCOUNT_NAME
```

#### Pipelines File
The `/services/otel_collector/pipelines.yaml` file contains the OTEL Collector pipelines configuration
[/services/otel_collector/pipelines.yaml](https://github.com/f5devcentral/application-study-tool/blob/main/services/otel_collector/pipelines.yaml):
```yaml
metrics/bigip:
  exporters:
  - otlphttp/metrics-bigip
  - debug/bigip
  processors:
  - batch/local
  receivers:
  - bigip/1
```


These are mapped into the final OTEL Collector config via the "file" directives in the
receivers and services.pipelines section of the
[/services/otel_collector/defaults/bigip-scraper-config.yaml](https://github.com/f5devcentral/application-study-tool/blob/main/services/otel_collector/defaults/bigip-scraper-config.yaml) file:

```
receivers: ${file:/etc/otel-collector-config/receivers.yaml}

processors:
  batch/local:

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


## Restart The AST Containers
Whenever the AST Configuration Files are updated, the containers need to be restarted for the updates
to take effect. This can be accomplished in a few ways, but the simplest is typically:

(From the project root directory)
```bash
$ docker compose down
$ docker compose up -d
```