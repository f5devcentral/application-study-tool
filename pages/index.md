---
layout: home
---
# Seven Layer Cake

### Overview
The Application Study Tool is intended to provide enhanced insights into (classic) BIG-IP products, leveraging best in class
open source telemetry tools. The full installation includes:

* Custom Instance of OpenTelemetry Collector with enhanced BIG-IP data receivers (data fetched via iControlRest) [Receiver Metrics Info](./receiver_metrics.md).
* Prometheus timeseries database for storing and querying collected data.
* Grafana Instance with pre-configured dashboards for quick insights at the device and "fleet" levels.

The Application Study Tool has everything needed to quickly get up and running with application insights at less than
production levels of reliability. For production/operational use cases, you can build on the included components,
accounting for things like high availability, enhanced security via e.g. Grafana OIDC integration, and similar. Alternatively,
the Openetlemetry Collector can be configured to send data to existing production ops monitoring tools as desired.

![](./assets/ui.gif)

### Table of Contents

- [Quick Start](./quickstart.md)
    - []
- [Dashboards](./dashboard.md)
    - [Fleet](./dashboard.md#fleet-dashboards)
        - [Inventory](./dashboard.md#inventory)
        - [Device Utilization](./dashboard.md#device-utilization)
        - [Virtual Servers](./dashboard.md#virtual-servers)
        - [SSL Certs](./dashboard.md#ssl-certs)
    - [Device](./dashboard.md#device-dashboards)
        - [Overview](./dashboard.md#overview)
        - [Top N](./dashboard.md#top-n)
        - [Pools](./dashboard.md#pools)
        - [Virtual Servers](./dashboard.md#virtual-servers-1)
        - [iRules](./dashboard.md#irules)
        - [WAF](.dashboard.)
    - [Profile](./dashboard.md#profile-dashboards)
        - [HTTP](./dashboard.md#http)
    - [Stats](./dashboard.md#collector-stats)
- [Config Management Overview](./config_management.md)
- [Config Migration (From v0.5.0 and Earlier)](./config_migration.md)
- [Receiver Metrics Info](./receiver_metrics.md)
- [Receiver Readme](./receiver_readme.md)
- [Metric Obfuscation](./metric_obfuscation.md)


 