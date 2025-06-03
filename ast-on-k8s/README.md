# Running the Application Study Tool in Kubernetes

This directory contains the manifest files for running the Application Study Tool in a Kubernetes cluster.
I used Kompose (https://kompose.io/) to create the initial YAML files, but needed to make changes for this to actually work in a production-grade Kubernetes cluster:
- Added permissions
- Created the needed configmaps and secrets

To just clone this directory (./ast-on-k8s), where the Kubernetes manifest files are located, you can follow these steps:
```
mkdir ast-on-k8s 
cd ast-on-k8s 
git init 
git remote add -f origin https://github.com/javajason/ast-config-wizard 
git config core.sparseCheckout true 
echo “ast-on-k8s/“ >> .git/info/sparse-checkout 
git pull origin main 
```

You will also need to modify the following files, at minimum.
- env-configmap.yaml:
  Update the Grafana credentials to the desired credentials and the SENSOR_ID/SENSOR_SECRET_TOKEN if using the global AST dashboard.
- env-device-secrets-configmap.yaml:
  Update the BIGIP_PASSWORD_1 value to the password of your BIG-IPs. If there are multiple BIG-IP passwords, also update BIGIP_PASSWORD_2, BIGIP_PASSWORD_3, BIGIP_PASSWORD_4, etc. (TODO: This needs to be changed so these passwords are stored as Kubernetes secrets.)
- otel-collector-deployment.yaml:
  This file has two environment variables that represent BIG-IP passwords, BIGIP_PASSWORD_1 and BIGIP_PASSWORD_2. If you have more than two BIG-IP passwords, you will need to add them here.
- rec-pipe-configmap.yaml:
  This is the equivalent of the services/otel_collector/receivers.yaml file. You will need to list all BIG-IPs to be monitored, along with their settings, in this file. You will also need to reference the BIG-IPs (i.e., "bigip/1", "bigip/2", etc.) in the receivers subsection under pipelines.yaml section (also in this file).

Other files in this directory can also be modified for additional customization. See the original repo (https://github.com/f5devcentral/application-study-tool) for specific customization guidance.

Deploy the AST application on Kubernetes using the following command. This requires the _kubectl_ client to be installed ahead of time and configured to connect and authenticate with your Kubernetes cluster.
```
kubectl create -f .
```

To verify AST has been successfully deployed, run the following command:
```
kubectl get pods
```
You should see output similar to the following:
```
$ kubectl get pods
NAME                              READY   STATUS    RESTARTS   AGE
grafana-54c8bbb46b-kf8fv          1/1     Running   0          2m14s
otel-collector-5b87d546b6-rnkml   1/1     Running   0          2m13s
prometheus-69cbc96779-vcrhz       1/1     Running   0          2m13s
```

So far, it has been tested on the following platforms:
- Azure Kubernetes Services (AKS)
- F5 Distributed Cloud vK8s (with some additional configuration - docs coming soon).

For the above platforms, you will want to create cloud-based loadbalancers to be able to access the Grafana and Prometheus services from the outside. The extras/ directory contains example manifest files for this.
