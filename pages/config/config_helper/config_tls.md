---
layout: page
title: Configure TLS
parent: Configuration Helper (Recommended)
grandparent: Configuration
nav_order: 5
---

### Configure CA File
AST expects a valid TLS cert bundle unless `tls.insecure_skip_verify` is
set to true for each device. In order to mount and use your CA file, you must
configure the docker-compose.yaml file in the root directory, and set the `ca_file` parameter to
the resulting path. Example:

docker-compose.yaml:
```yaml
  otel-collector:
    volumes:
      - ./services/otel_collector:/etc/otel-collector-config
      - ./config/ca_bundle.pem:/etc/ssl/ca_bundle.pem
```

config/ast_defaults.yaml (or the tls section of each device in config/bigip_receivers.yaml):
```yaml
bigip_receiver_defaults:
  tls:
    insecure_skip_verify: false
    ca_file: "/etc/ssl/ca_bundle.pem"
```

The configuration parameter `tls.insecure_skip_verify` defaults to false. Installers
who would like to opt-in to run in an insecure TLS mode must set
`tls.insecure_skip_verify: true` and understand
that the connection between the OTEL collector and the BIG-IP does not have secure
TLS termination.
