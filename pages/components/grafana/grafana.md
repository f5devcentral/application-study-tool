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

### Import AST Dashboards into Your Own Grafana Instance
If you have your own (non-AST) Grafana instance and would like to display AST dashboards from your instance, follow these steps:

#### Connect your Grafana instance to the AST Prometheus instance.
- In the menu bar on the left, click Connections >> Data sources. 
- If this is a new instance of Grafana, the “Add data source” button will appear in the middle of the screen. If this is an existing instance with pre-existing data sources, the button will be in the upper-right corner of the screen and will say “Add new data source”. Either way, click on it.
- Select Prometheus from the list of data sources. You may have to scroll down or enter “prometheus” in the search bar. 
- Fill in a name (for example, “ast-prometheus”), and the URL/IP address to get to the Prometheus instance. (Unless the port for the AST instance of Prometheus was modified, it will be the default of 9090.) 
- The “Interval behaviour >> Scrape interval” is set to 15s by default. This will work but, if you want to save connections, you can set it to 60s. 
- Click the blue "Save & test" button and ensure you get the message, “Successfully queried the Prometheus API.” at the bottom of the screen. 

#### Import the Dashboard Configuration
- Click on “Dashboards” in the menu on the left. 
- Click the blue “New” button in the upper-right and, from the drop-down, select "Import". 
- If you have saved the dashboard you wish to import as a JSON file export, click on "Upload dashboard JSON file" and upload the JSON file you exported. If you just copied the JSON contents, you can paste it in the "Import via dashboard JSON model" box below.
- Give the dashboard a name (under Name). 
- Under the Prometheus drop-down, select your Prometheus data source.
- Click Import.

You will now see the new dashboard in your own Grafana instance.
