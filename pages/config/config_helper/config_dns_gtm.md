---
layout: page
title: Configure DNS & GTM (Optional)
parent: Configuration Helper (Recommended)
grandparent: Configuration
nav_order: 6
---

## DNS and GTM Metrics

By default, settings for the  collection of DNS and GTM metrics are disabled. They add a relatively large number of
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
  # Enable DNS and/or GTM collection for this device:
  data_types:
    f5.dns:
      enabled: true
    f5.gtm:
      enabled: true
  # ...
```

### Enable For All devices
Edit the `/config/ast_defaults.yaml` and add the following data_types configs for the desired devices:

```yaml
bigip_receiver_defaults:
  # ...
  # Enable DNS and/or GTM collection for all devices:
  data_types:
    f5.dns:
      enabled: true
    f5.gtm:
      enabled: true
  # ...
```