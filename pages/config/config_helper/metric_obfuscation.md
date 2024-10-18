---
layout: page
title: Metric Obfuscation
parent: Configuration Helper (Recommended)
grandparent: Configuration
nav_order: 4
---
# Metric Obfuscation

Metric data can be obfuscated before sending to storage systems (local Prometheus, F5 Datafabric,
or your Org metrics store) using the built-in functionality in the Opentelemetry Collector processors.


{: .important }
The config helper script must run after any changes to the default or device specific configs,
and the Otel container restarted before changes will take effect.

The Application Study Tool Opentelemetry Collector includes the following data processors which can
be used to manipulate data before it's exported:

* `Transform Processor` [README](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/processor/transformprocessor/README.md)
* `Resource Processor` - [README](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/processor/resourceprocessor/README.md)
* `Metrics Transform Processor` - [README](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/processor/metricstransformprocessor/README.md)
* `Attributes Processor` - [README](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/processor/attributesprocessor/README.md)
* `Filter Processor` - [README](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/processor/filterprocessor/README.md)

## Masking Attributes Example
The attributes processor can be used to hash metric attributes before they're exported. 

To enable this functionality for data being exported to F5:

1. Add an attributes processor config as shown to 
[services/otel_collector/defaults/bigip-scraper-config.yaml](https://github.com/f5devcentral/application-study-tool/blob/main/services/otel_collector/defaults/bigip-scraper-config.yaml)


(This example will mask the f5.instance.management_ip and f5.node.ip_address fields):
```yaml
processors:
...
  attributes/mask-some-attributes:
    actions:
      - key: f5.instance.management_ip
        action: hash
      - key: f5.node.ip_address
        action: hash
```

2. Edit the [config/ast_defaults.yaml](https://github.com/f5devcentral/application-study-tool/blob/main/config/ast_defaults.yaml) file to include the new processor
on the F5 Datafabric pipeline:
```yaml
pipelines:
...
  metrics/f5-datafabric:
    # receivers list are generated via the config helper script
    # Adding attributes/mask-some-attributes to the list of enabled processors.
    processors: [interval/f5-datafabric, attributes/mask-some-attributes, attributes/f5-datafabric, batch/f5-datafabric]
    exporters: [otlp/f5-datafabric, debug/bigip]
...
```