---
layout: page
title: Prometheus
nav_order: 1
parent: Components
has_children: true
permalink: /components/prometheus
---

# Prometheus Integration in Application Study Tool

The **Application Study Tool (AST)** leverages **Prometheus**, a powerful time series database, to collect and visualize metric data from F5 BigIP devices through an OpenTelemetry collector.

## Configuration

To customize your Prometheus setup, you can modify the Prometheus configuration file located at:

```
/services/prometheus/prometheus.yaml
```

For detailed guidance on the configuration options available, refer to the [Prometheus Configuration Documentation](https://prometheus.io/docs/prometheus/latest/configuration/configuration/).

## Accessing Prometheus

You can access the Prometheus service directly on port **9090** of the host where the Application Study Tool is running.

## Querying Metrics

For querying the metrics collected by Prometheus, either directly or by editing Grafana dashboar panels,
see the [Prometheus Query Syntax Documentation](https://prometheus.io/docs/prometheus/latest/querying/basics/).

## Storage Sizing

When scoping out the AST server where your Prometheus instance will run, it's important to consider its
storage and memory requirements, as it is the largest consumer of disk and memory resources in the AST
project. 

A single modestly sized server can accommodate many BigIP Devices, but exact specs will depend heavily on
how the devices are configured, storage retention settings, etc.

For guidance on instance storage sizing, please review the [Prometheus Storage Sizing Documentation](https://prometheus.io/docs/prometheus/1.8/storage/).

