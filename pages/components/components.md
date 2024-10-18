---
layout: page
title: Components
nav_order: 4
has_children: true
permalink: /components
---

# Components

The Application Study Tool is built using best-of-breed open source components, allowing for 
flexibility, community support, and continuous improvement. By leveraging established technologies like 
Grafana, Prometheus, and OpenTelemetry, the AST ensures a reliable and robust method for collecting and
visualizing data from BigIP devices.

## Grafana

[**Grafana**](https://grafana.com/docs/grafana/latest/) serves as the visualization layer for the Application Study Tool, allowing users to create and manage dashboards that display metrics collected from F5 BigIP devices. With its powerful querying capabilities and customizable visualizations, Grafana enables users to gain insights into application performance and operational metrics effectively.

## Prometheus

[**Prometheus**](https://prometheus.io/docs/introduction/overview/) is the time series database utilized within the Application Study Tool to store and manage metric data. It collects data emitted by the OpenTelemetry Collector and provides powerful querying capabilities for analysis. Prometheus is designed for reliability and scalability, making it the backbone of metric storage for many monitoring applications.

## OpenTelemetry Collector

The [**OpenTelemetry Collector**](https://opentelemetry.io/docs/collector/) is a custom distribution integrated into the Application Study Tool that collects metrics from F5 BigIP devices. Featuring a **BigIP Receiver** component, it retrieves data from the BigIP iControl REST endpoint and transforms it into OpenTelemetry metrics. This data is then forwarded to Prometheus for storage and visualization, ensuring seamless integration across the monitoring stack.
