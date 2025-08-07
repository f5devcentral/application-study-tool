---
layout: page
title: Configure Export To F5 Datafabric
parent: Configuration Helper (Recommended)
grandparent: Configuration Management
nav_order: 3
---

## Configure Periodic Metric Data Export To F5

1. TOC
{:toc}

The application study tool can be configured to periodically (every 5 minutes) export a snapshot of your
BigIP metrics to F5. Contact your F5 Sales Representative for a "Sensor ID" (a unique string used to 
associate your metrics with your Organization) and a "Sensor Secret Token" (used to authenticate to the 
F5 Datafabric as an authorized data sender for your Org).

{: .important }
The config helper script must run after any changes to the default or device specific configs,
and the otel container restarted before changes will take effect.

This functionality is enabled as follows:

### Enable the flag in /config/ast_defaults.yaml file as follows:

```yaml
# Set this true to enable periodic metric export to F5 DataFabric.
# Requires adding your sensor ID and secret token to the container environment (see .env-example).
# Contact your F5 sales rep to obtain the ID / secret token.
f5_data_export: true
```

### Add the Sensor ID and Secret Token to the .env file
Contact your F5 Sales Representative for a "Sensor ID" (a unique string used to 
associate your metrics with your Organization) and a "Sensor Secret Token" (used to authenticate to the 
F5 Datafabric as an authorized data sender for your Org).

```bash
$ cp .env-example .env
$ cat .env
# Optional Parameters Required for metrics export to F5 DataFabric
SENSOR_SECRET_TOKEN="YOUR_TOKEN"
SENSOR_ID="YOUR_ID"
$ vi .env
```

Finally, [Run The Configuration Helper]({{ site.url }}{{ site.baseurl }}/config/config_helper) and restart the project containers.