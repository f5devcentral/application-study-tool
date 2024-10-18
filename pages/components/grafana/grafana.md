---
layout: page
title: Grafana
nav_order: 1
parent: Components
has_children: true
permalink: /components/grafana
---

## Grafana In AST

The Application Study Tool leverages Grafana for visualization of all collected metrics stored in 
prometheus.

The instance is pre-configured with dashboards built by the AST team to provide insights into the fleet
of BigIP devices being monitored. Grafana is a flexible visualization tool, and AST users are encouraged
to customize the 'out of the box' dashboards or build new views around the AST data that suit your 
specific organization's workflows.


### Configure Grafana Settings

The **Grafana** instance within the **Application Study Tool (AST)** can be easily configured using 
environment variables, following the standard [Grafana configuration options](https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/#override-configuration-with-environment-variables). This 
flexibility allows you to tailor your Grafana setup to meet your specific requirements 
(e.g. authentication integration, TLS, and other settings required)

#### Passing Environment Variables To The Instance

The included docker-compose file looks for a .env file at the root of the project directory and will
mount that at start time. Variables can be added / modified here, or in the docker-compose file directly
using the standard docker-compose syntax for container environment

```bash
$ cat .env-example 
# Grafana Environment Variables
# These should be updated to more secure values outside of testing environments.
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=admin
$ cp .env-example .env
$ vi .env
```

### Modify Grafana Views
The AST team will maintain a set of dashboards that cover a wide variety
of use-cases, but for needs that have less broad applicability or to suit particular tastes
(e.g. bar-chart vs pie-chart), users are encouraged to modify or create new views into the AST data.

By default, all dashboards within an AST instance are open to editing directly via the ui. Follow the
[instructions](https://grafana.com/docs/grafana/latest/dashboards/) from grafana for building or editing
dashboards, visualizations, etc.

### Save Grafana Views Outside Docker Volume
Saving a dashboard view in the Grafana UI will write it to the docker volume for persistence across
container restarts. In order to persist dashboards outside the docker environment, you can export them as
JSON following these 
[instructions](https://grafana.com/docs/grafana/latest/dashboards/share-dashboards-panels/#export-a-dashboard-as-json).

You can save dashboard files under /services/grafana/provisioning/dashboards from the project root to
automatically load them when the container is started.