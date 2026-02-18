---
layout: page
title: BIG-IP API Endpoints
parent: OTEL Collector
grand_parent: Components
nav_order: 3
---

# BIG-IP iControl REST API Endpoints

This page documents the iControl REST API calls the AST BigIP Receiver makes against each BIG-IP
device during a collection cycle.

> **Note:** The BigIP Receiver source code is distributed as a pre-built Docker image
> (`ghcr.io/f5devcentral/application-study-tool/otel_custom_collector`) and is not included in this
> repository. The endpoint paths listed here are derived from the receiver's configuration schema and
> observed runtime metrics. See [Source of Truth](#source-of-truth) below for how to verify them
> against a live deployment.

1. TOC
{:toc}

---

## Authentication

Every collection cycle begins with a token request to obtain a session token:

```
POST https://<bigip-mgmt-ip>/mgmt/shared/authn/login
```

All subsequent requests in that cycle use the returned token for authentication.

---

## General API Pattern

After authentication, the receiver calls iControl REST endpoints under `/mgmt/tm/`:

```
GET https://<bigip-mgmt-ip>/mgmt/tm/<module>/<resource>?$top=<page_item_limit>&$skip=<offset>
```

Key defaults:

| Setting | Default | Config Key |
|---------|---------|------------|
| Management port | `443` | `endpoint` |
| Items per page | `10,000` | `page_item_limit` |
| TLS verification | Enabled | `tls.insecure_skip_verify` |
| Concurrent API workers | `2` | `concurrent_workers` |

---

## Data Types and Expected API Paths

Each **data type** corresponds to one or more iControl REST API calls. The exact paths per data type
are tracked at runtime as the `path` label on the `endpoint.scrape.*` collector metrics (see
[Receiver Metrics]({{ site.url }}{{ site.baseurl }}/components/otel_collector/receiver_metrics.html)).

### Enabled by Default

| Data Type | BIG-IP Module / Expected API Path |
|-----------|-----------------------------------|
| `f5.collector` | Internal OTEL collector metrics only — no BIG-IP API call |
| `f5.license` | `/mgmt/tm/sys/license` |
| `f5.module` | `/mgmt/tm/sys/module` |
| `f5.nethsm` | `/mgmt/tm/sys/nethsm` |
| `f5.network` | `/mgmt/tm/net/...` (interfaces, routes, VLANs, etc.) |
| `f5.node` | `/mgmt/tm/ltm/node` |
| `f5.plane` | `/mgmt/tm/sys/management-ip` and related management-plane endpoints |
| `f5.policy.eviction` | `/mgmt/tm/ltm/eviction-policy` |
| `f5.policy.bandwidth_control` | `/mgmt/tm/net/bwc/policy` |
| `f5.pool` | `/mgmt/tm/ltm/pool` |
| `f5.profile.client_ssl` | `/mgmt/tm/ltm/profile/client-ssl` |
| `f5.profile.server_ssl` | `/mgmt/tm/ltm/profile/server-ssl` |
| `f5.profile.fasthttp` | `/mgmt/tm/ltm/profile/fasthttp` |
| `f5.profile.fastl4` | `/mgmt/tm/ltm/profile/fastl4` |
| `f5.profile.http` | `/mgmt/tm/ltm/profile/http` |
| `f5.profile.one_connect` | `/mgmt/tm/ltm/profile/one-connect` |
| `f5.profile.quic` | `/mgmt/tm/ltm/profile/quic` |
| `f5.profile.udp` | `/mgmt/tm/ltm/profile/udp` |
| `f5.profile.tcp` | `/mgmt/tm/ltm/profile/tcp` |
| `f5.profile.http2` | `/mgmt/tm/ltm/profile/http2` |
| `f5.profile.http3` | `/mgmt/tm/ltm/profile/http3` |
| `f5.profile.web_acceleration` | `/mgmt/tm/ltm/profile/web-acceleration` |
| `f5.rule` | `/mgmt/tm/ltm/rule` |
| `f5.ssl_certificate` | `/mgmt/tm/sys/crypto/cert` |
| `f5.system` | `/mgmt/tm/sys/cpu`, `/mgmt/tm/sys/memory`, `/mgmt/tm/cm/failover-status` |
| `f5.virtual_server` | `/mgmt/tm/ltm/virtual` |

### Disabled by Default (Opt-In Required)

These data types must be explicitly enabled in `config/ast_defaults.yaml` or in the per-device
`config/bigip_receivers.yaml`. See
[Configuration]({{ site.url }}{{ site.baseurl }}/config/config_helper/config_dns_gtm.html) for instructions.

| Data Type | BIG-IP Module / Expected API Path |
|-----------|-----------------------------------|
| `f5.policy.api_protection` | `/mgmt/tm/apm/policy/api-protection` |
| `f5.policy.asm` | `/mgmt/tm/asm/policies` |
| `f5.policy.firewall` | `/mgmt/tm/security/firewall/policy` |
| `f5.policy.ip_intelligence` | `/mgmt/tm/security/ip-intelligence` |
| `f5.policy.nat` | `/mgmt/tm/ltm/nat` |
| `f5.profile.dos` | `/mgmt/tm/ltm/profile/dos` |
| `f5.apm` | `/mgmt/tm/apm/...` |
| `f5.cgnat` | `/mgmt/tm/cgnat/...` |
| `f5.dns` | `/mgmt/tm/ltm/dns/...` |
| `f5.dos` | `/mgmt/tm/security/dos/...` |
| `f5.firewall` | `/mgmt/tm/security/firewall/...` |
| `f5.gtm` | `/mgmt/tm/gtm/...` |

---

## Observing Actual Paths at Runtime

Because each API call is tracked as a labeled metric, the exact paths hit on a live device can be
read directly from Prometheus after the stack is running.

Query all scrape request counts with their paths:

```promql
endpoint_scrape_requests_total
```

The `path` label on each time series shows the exact URL path used for that iControl REST call.
You can also filter by device or data type using the `dataType` label:

```promql
endpoint_scrape_requests_total{dataType="f5.virtual_server"}
```

The related metrics (`endpoint.scrape.duration`, `endpoint.scrape.response.size`,
`endpoint.scrape.response.status`) use the same `path` label and are documented in
[Receiver Metrics]({{ site.url }}{{ site.baseurl }}/components/otel_collector/receiver_metrics.html).

---

## Source of Truth

The definitive list of API paths is compiled from the BigIP Receiver source code, which is
maintained in a separate F5 GitLab repository and distributed as a pre-built Docker image. The
paths listed on this page are the best approximation available from receiver configuration schemas
and runtime metric observation.

To verify or enumerate all paths for a running deployment, use the Prometheus queries above. The
`path` label is set by the receiver itself and reflects the exact URL path sent to the BIG-IP.
