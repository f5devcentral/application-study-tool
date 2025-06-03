# Running the Application Study Tool in Kubernetes

This directory contains the manifest files for running the Application Study Tool in a Kubernetes cluster.
I used Kompose (https://kompose.io/) to create the initial YAML files, but needed to make changes for this to actually work in a production-grade Kubernetes cluster:
- Added permissions
- Created the needed configmaps and secrets from the config files used by the Docker Compose version of AST.
- Modifying some of the mount paths to work in a Kubernetes cluster

To clone only this directory (./ast-on-k8s), where the Kubernetes manifest files are located, follow these steps:
```
git init 
git clone -n --depth=1 --filter=tree:0 https://github.com/javajason/ast-config-wizard/
cd ast-config-wizard
git sparse-checkout set --no-cone /ast-on-k8s
git checkout
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

Note that this creates and runs the Application Study Tool in a Kubernetes environment and includes the NodePort services for Grafana and Prometheus for external access.
Depending on your connection to the cluster and connectivity requirements, a NodePort might be sufficient. However, most Internet-facing applications use a more robust ingress solution, such as a cloud loadbalancer or an F5 BIG-IP with CIS.
The ./extras directory contains example manifest files for a loadbalancer config in AKS.

In the meantime, you can test that everything is running correctly by accessing Grafana though the NodePort service. First, get the NodePort port number with the following command:
```
kubectl get svc
```
You should see output similar to the following:
```
$ kubectl get svc
NAME           TYPE           CLUSTER-IP      EXTERNAL-IP                            PORT(S)          AGE
graf-service   NodePort       192.168.1.188   <none>                                 3000:31034/TCP   96m
grafana        ClusterIP      192.168.1.18    <none>                                 3000/TCP         96m
kubernetes     ClusterIP      192.168.1.1     <none>                                 443/TCP          718d
openshift      ExternalName   <none>          kubernetes.default.svc.cluster.local   <none>           718d
prom-service   NodePort       192.168.1.101   <none>                                 9090:32300/TCP   96m
prometheus     ClusterIP      192.168.1.221   <none>                                 9090/TCP         96m
```

So far, this has been tested on the following platforms:
- Azure Kubernetes Services (AKS)
- F5 Distributed Cloud vK8s (with some additional configuration - docs coming soon).
- RedHat OpenShift
