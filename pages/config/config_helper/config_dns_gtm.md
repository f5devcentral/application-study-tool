---
layout: page
title: Configure Optional Metrics
parent: Configuration Helper (Recommended)
grandparent: Configuration Management
nav_order: 6
---

## Optional Metrics

By default, settings for the  collection of some less common module metrics are disabled. They add a relatively large number of
additional API calls, and since many devices may not have these features enabled, it was determined to
make them 'opt in'.

They can be enabled on a device by device basis (in `/config/bigip_receivers.yaml`),
or globally (in `/config/ast_defaults.yaml`) as follows:

{: .important }
The config helper script must run after any changes to the default or device specific configs,
and the otel container restarted before changes will take effect.

### Enable For Specific devices
Edit the `/config/bigip_receivers.yaml` and add the following data_types configs for the desired devices:

```yaml
bigip/1:
  endpoint: https://10.0.0.1
  # ...
  # Enable optional modules by setting any to true
  data_types:
    f5.apm:
      enabled: false
    f5.cgnat:
      enabled: false
    f5.dns:
      enabled: false
    f5.dos:
      enabled: false
    f5.firewall:
      enabled: false
    f5.gtm:
      enabled: false
    f5.policy.api_protection:
      enabled: false
    f5.policy.asm:
      enabled: false
    f5.policy.firewall:
      enabled: false
    f5.policy.ip_intelligence:
      enabled: false
    f5.policy.nat:
      enabled: false
    f5.profile.dos:
      enabled: false
  # ...
```

### Enable For All devices
Edit the `/config/ast_defaults.yaml` and add the following data_types configs for the desired devices:

```yaml
bigip_receiver_defaults:
  # ...
  # Enable optional modules for all devices:
  data_types:
    f5.apm:
      enabled: false
    f5.cgnat:
      enabled: false
    f5.dns:
      enabled: false
    f5.dos:
      enabled: false
    f5.firewall:
      enabled: false
    f5.gtm:
      enabled: false
    f5.policy.api_protection:
      enabled: false
    f5.policy.asm:
      enabled: false
    f5.policy.firewall:
      enabled: false
    f5.policy.ip_intelligence:
      enabled: false
    f5.policy.nat:
      enabled: false
    f5.profile.dos:
      enabled: false
  # ...
```