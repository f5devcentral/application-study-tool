---
layout: page
title: Std Otel Collector Config
parent: Manual Configuration
grandparent: Configuration Management
nav_order: 2
---

## Manual Configuration With Default Otel Collector Settings File

1. TOC
{:toc}

The Otel Collector container points to a single configuration file that is loaded at startup.
This config file, by default, loads a list of receivers and pipelines from elsewhere in the directory
structure.

The other configuration managent options modify these other files, but the primary config
can also be managed however you see fit.


{: .important }
The OTEL Collector Container must be restarted before changes to these files will take effect.

The main otel collector config file is located in `/services/otel_collector/defaults/bigip-scraper-config.yaml`

Syntax for these files is the [Opentelemetry Collector Configuration](https://opentelemetry.io/docs/collector/configuration/) syntax.

```yaml
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