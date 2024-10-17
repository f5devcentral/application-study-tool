---
layout: page
title: BigIP Receiver Readme
parent: OTEL Collector
grand_parent: Components
nav_order: 1
---

# F5 Big-IP Receiver

This receiver fetches stats from a F5 Big-IP node using F5's [iControl REST API](https://clouddocs.f5.com/api/icontrol-rest).


1. TOC
{:toc}

## Prerequisites

This receiver supports Big-IP versions `11.6.5+`

## Configuration

The following settings are required:

- `username`
- `password`

The following settings are optional:

- `endpoint` (default: `https://localhost:443`): The URL of the Big-IP environment.
- `collection_interval` (default = `10s`): This receiver collects metrics on an interval. Valid time units are `ns`, `us` (or `µs`), `ms`, `s`, `m`, `h`.
- `tls` (defaults defined [here](https://github.com/open-telemetry/opentelemetry-collector/blob/main/config/configtls/README.md)): TLS control. By default insecure settings are rejected and certificate verification is on.
- `enable_http_client_metrics` (default = `false`): Enable collection of metrics for http client requests to the device.
- `page_item_limit` (default = 100): The number of objects per page for paginated api requests
- `concurrent_workers` (default = 2): The number of concurrent API requests per receiver.
- `data_types` (default: all enabled): This map allows you to enable / disable collection and sending of data by type. The list of available data types can be found in `./config.go`, in the DataTypesConfig struct definition.

### Example Configuration

```yaml
receivers:
  bigip:
    collection_interval: 10s
    endpoint: https://localhost:443
    username: otelu
    password: ${env:BIGIP_PASSWORD}
    tls:
      insecure_skip_verify: true
    enable_http_client_metrics: true
    concurrent_workers: 2
    page_item_limit: 100
    data_types:
      f5.profile.web_acceleration:
        enabled: false
        attribute_name: some_alternative_data_type_name
```

Available data_types:
```
f5.collector
f5.license
f5.module
f5.node
f5.plane
f5.policy.eviction
f5.policy.firewall
f5.policy.ip_intelligence
f5.policy.api_protection
f5.policy.bandwidth_control
f5.policy.nat
f5.pool
f5.profile.client_ssl
f5.profile.server_ssl
f5.profile.dos
f5.profile.fasthttp
f5.profile.fastl4
f5.profile.http
f5.profile.one_connect
f5.profile.quic
f5.profile.udp
f5.profile.tcp
f5.profile.http2
f5.profile.http3
f5.profile.web_acceleration
f5.rule
f5.ssl_certificate
f5.system
f5.virtual_server
f5.policy.asm
f5.dns                          ### DEFAULT DISABLE
f5.gtm                          ### DEFAULT DISABLE
```

TLS config is documented further under the [opentelemetry collector's configtls package](https://github.com/open-telemetry/opentelemetry-collector/blob/main/config/configtls/README.md).

## Metrics

Details about the metrics produced by this receiver can be found in [/docs/receiver_metrics.md](/docs/receiver_metrics.md)
