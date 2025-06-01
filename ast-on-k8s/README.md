# Running the Application Study Tool in Kubernetes

This directory contains the manifest files for running the Application Study Tool in a Kubernetes cluster

You will also need to modify the following files at minimum.
- env-configmap.yaml:
  Update the Grafana credentials to the desired credentials and the SENSOR_ID/SENSOR_SECRET_TOKEN if using the global AST dashboard.
- env-device-secrets-configmap.yaml:
  Update the BIGIP_PASSWORD_1 value to the password of your BIG-IPs. If there are multiple BIG-IP passwords, also update BIGIP_PASSWORD_2, BIGIP_PASSWORD_3, BIGIP_PASSWORD_4, etc.
- otel-collector-deployment.yaml:
  This file has two environment variables for BIG-IP passwords, BIGIP_PASSWORD_1 and BIGIP_PASSWORD_2. If you have more than two BIG-IP passwords, you will need to add them here.
- rec-pipe-configmap.yaml:
  This is the equivalent of the services/otel_collector/receivers.yaml file. You will need to list all BIG-IPs to be monitored, along with their settings, in this file. You will also need to reference the BIG-IPs (i.e., "bigip/1", "bigip/2", etc.) in the receivers section under pipelines.yaml (also in this file).

Other files in this directory can also be modified for additional customization. See the original repo (https://github.com/f5devcentral/application-study-tool) for specific customization guidance.


So far, it has been tested on the following platforms:
- Azure Kubernetes Services (AKS)
- F5 Distributed Cloud vK8s (with some additional configuration - docs coming soon).

For the above platforms, you will want to create cloud-based loadbalancers to be able to access the Grafana and Prometheus services from the outside. The extras/ directory contains example manifest files for this.
