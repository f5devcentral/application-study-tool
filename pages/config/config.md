---
layout: page
title: Configuration Management
nav_order: 3
has_children: true
permalink: /config
---


# AST Configuration Management Overview
This configuration section applies to the AST Opentelemetry Collector. For Grafana, Prometheus or other
components, see the corresponding documentation in [> Components]({{ site.url }}{{ site.baseurl }}/components)


## Config Management Options
In the post v0.6.0 management scheme, users can choose from one of the below options to manage
the AST Otel Collector configs:

1. Using a python script to generate full Otel Collector Config files from a small set of default
settings and per-device overrides (recommended for most users, and includes migration path from old big-ips.json configs). See [Configuration > Configuration Helper (Recommended)]({{ site.url }}{{ site.baseurl }}/config/config_helper) for details.

2. Manual maintenance of the Otel Collector Config Receivers and Pipelines files (recommended for 
advanced use cases or people with their own automation pipelines). See [Configuration > Manual Configuration > Receiver/Pipeline Config]({{ site.url }}{{ site.baseurl }}/config/manual_config/receivers_pipelines.html) for details.

3. Manual maintenance of the Otel Collector Config files in
[/services/otel_collector/defaults](https://github.com/f5devcentral/application-study-tool/blob/main/services/otel_collector/defaults). See [Configuration > Manual Configuration > Std Otel Collector Config]({{ site.url }}{{ site.baseurl }}/config/manual_config/default_otel.html) for details.


