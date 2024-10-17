---
layout: page
title: OTEL Collector
nav_order: 5
parent: Components
has_children: true
permalink: /components/otel_collector
---

The **OpenTelemetry Collector** is a crucial component of the **Application Study Tool (AST)**, 
providing a custom distribution designed specifically for monitoring F5 BigIP devices. This collector 
features a specialized **BigIP Receiver** component, which
retrieves metric data from the BigIP iControl REST endpoint.

While working towards open sourcing the receiver component, the AST project will maintain a build of the
collector with the requisite receivers, processors, and exporters needed to collect and send data where
required. If you have a particular exporter that you'd like included in this list, please open a support
issue.

## Custom Collector Components

### Exporters
* [OTLPExporter](https://github.com/open-telemetry/opentelemetry-collector/tree/main/exporter/otlpexporter)
* [OTLPHTTPExporter](https://github.com/open-telemetry/opentelemetry-collector/blob/main/exporter/otlphttpexporter/README.md)
* [DebugExporter](https://github.com/open-telemetry/opentelemetry-collector/tree/main/exporter/debugexporter)
* [PrometheusRemoteWriteExporter](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/exporter/prometheusremotewriteexporter)
* [LokiExporter](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/exporter/lokiexporter/README.md)
* [ClickHouseExporter](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/exporter/clickhouseexporter)

### Receivers
* [OTLPReceiver](https://github.com/open-telemetry/opentelemetry-collector/tree/main/receiver/otlpreceiver)
* [PrometheusReceiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/prometheusreceiver)
* [SyslogReceiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/syslogreceiver)
* [AST BigIPReceiver](https://github.com/f5devcentral/application-study-tool/)

### Processors
* [BatchProcessor](https://github.com/open-telemetry/opentelemetry-collector/blob/main/processor/batchprocessor/README.md)
* [TransformProcessor](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/transformprocessor)
* [ResourceProcessor](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/resourceprocessor)
* [MetricsTransformProcessor](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/metricstransformprocessor)
* [AttributesProcessor](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/attributesprocessor)
* [FilterProcessor](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/filterprocessor)
* [IntervalProcessor](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/intervalprocessor)

### Extensions
* [BasicAuthExtension](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/extension/basicauthextension)
* [BearerTokenAuthExtension](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/extension/bearertokenauthextension)