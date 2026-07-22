# Configuration

Files in this directory can be used to configure aspects of the Application Study Tool.

For additional detail, see:

* [Configuration Management](pages/config_management.md) (new users start here)

## Environment Label

The `environment` field allows grouping devices by environment (e.g. production, staging, lab).
When set, an `environment` label is added to all metrics from that device, and Grafana dashboards
provide an Environment dropdown to filter by this label.

**Usage in `bigip_receivers.yaml`:**

```yaml
bigip/1:
  environment: production
  endpoint: https://10.240.7.235
  ...

bigip/2:
  environment: staging
  endpoint: https://10.240.7.236
  ...
```

If not specified, devices inherit the default from `ast_defaults.yaml` (currently `production`).
The field is optional and fully backward-compatible.
