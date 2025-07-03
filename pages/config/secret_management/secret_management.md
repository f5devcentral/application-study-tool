---
layout: page
title: Secrets Management
parent: Configuration Management
nav_order: 4
---

# BigIP Device Secrets Management

Application Study Tool's Opentelemetry Collector requires credentials to access the BigIP devices
being monitored. The default configuration (management via environment variable file on disk)
is optimized for quick proof of concept style deployment, and is unlikely to meet the
"production" level use case requirements in many organizations.

This section describes the default configuration (via env file), and outlines alternate
approaches which may be more appropriate for actual production use cases (at a high
level since the details will depend heavily on provider selection, deployment environment,
etc).
