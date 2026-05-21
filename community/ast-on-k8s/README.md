# Running the Application Study Tool in Kubernetes

This directory contains the manifest files for running the Application Study Tool in a Kubernetes cluster.

To clone only this directory (./community/ast-on-k8s), where the Kubernetes manifest files are located, follow these steps:
```
git init 
git clone -n --depth=1 --filter=tree:0 https://github.com/f5devcentral/application-study-tool/
cd application-study-tool
git sparse-checkout set --no-cone /community/ast-on-k8s
git checkout
cd community/ast-on-k8s
```

You will also need to modify the following files, at minimum.
- env-configmap.yaml
  
  Update the Grafana credentials to the desired credentials and the SENSOR_ID/SENSOR_SECRET_TOKEN if using the global AST dashboard.
- env-device-secrets-configmap.yaml
  
  Update the BIGIP_PASSWORD_1 value to the password of your BIG-IPs. If there are multiple BIG-IP passwords, also update BIGIP_PASSWORD_2, BIGIP_PASSWORD_3, BIGIP_PASSWORD_4, etc. (TODO: This needs to be changed so these passwords are stored as Kubernetes secrets.)
- otel-collector-deployment.yaml
  
  This file has two environment variables that represent BIG-IP passwords, BIGIP_PASSWORD_1 and BIGIP_PASSWORD_2. If you have more than two BIG-IP passwords, you will need to add them here.
- rec-pipe-configmap.yaml
  
  This is the equivalent of the services/otel_collector/receivers.yaml file. You will need to list all BIG-IPs to be monitored, along with their settings, in this file (within the "receivers.yaml" section). The following is an example that shows how to include two BIG-IP devices. (Additional devices would be added to the end as bigip/3, bigip/4, etc.)

```
  receivers.yaml: |
    bigip/1:
      collection_interval: 60s
      data_types:
        f5.apm:
          enabled: true
        ...
      endpoint: https://10.1.1.5
      password: ${env:BIGIP_PASSWORD_1}
      timeout: 60s
      tls:
        ca_file: ''
        insecure_skip_verify: true
      username: admin
    bigip/2:
      collection_interval: 60s
      data_types:
        f5.apm:
          enabled: false
        ...
      endpoint: https://10.1.1.15
      password: ${env:BIGIP_PASSWORD_1}
      timeout: 60s
      tls:
        ca_file: ''
        insecure_skip_verify: true
      username: admin
  ```

  You will also need to ensure reference to these devices are included in the list of BIG-IPs (i.e., "bigip/1", "bigip/2", etc.) in the receivers subsection under "pipelines.yaml" section (also in this file). The "pipelines.yaml" section of this file will look like the following:
```
  pipelines.yaml: |
    metrics/local:
      exporters:
      - otlphttp/metrics-local
      - debug/bigip
      processors:
      - batch/local
      receivers:
      - bigip/1
      - bigip/2
      - bigip/3
      ...
```

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
NAME                              READY   STATUS    RESTARTS   AGE
grafana-54c8bbb46b-kf8fv          1/1     Running   0          2m14s
otel-collector-5b87d546b6-rnkml   1/1     Running   0          2m13s
prometheus-69cbc96779-vcrhz       1/1     Running   0          2m13s

(other pods may be listed here as well)
```

Make sure the three AST pods, with names beginning with grafana, otel-collector, and prometheus, have a STATUS of "Running". If so, the Application Study Tool is now running in a Kubernetes environment. This collection also creates [NodePort](https://kubernetes.io/docs/concepts/services-networking/service/#type-nodeport) services for Grafana and Prometheus for external access. NodePorts use high port numbers (30000 and up) which may be sufficient, depending on your connection to the cluster and connectivity requirements. However, most Internet-facing applications use more robust ingress solutions, such as cloud loadbalancers and F5 BIG-IPs with the [Container Ingress Services](https://clouddocs.f5.com/containers/latest/) (CIS) plugin. These solutions are also able to expose the application to the more common ports, 80 (HTTP) and 443 (HTTPS).

The ./extras directory contains example manifest files for a loadbalancer config in AKS.

In the meantime, you can verify that everything is working correctly by accessing Grafana though the NodePort service. You will need connectivity between your web browser and one of the worker nodes.
To access this service, first get the NodePort port number using the following command:
```
kubectl get svc
```
You should see output similar to the following:
```
NAME           TYPE           CLUSTER-IP      EXTERNAL-IP                            PORT(S)          AGE
graf-service   NodePort       192.168.1.188   <none>                                 3000:31034/TCP   96m
grafana        ClusterIP      192.168.1.18    <none>                                 3000/TCP         96m
kubernetes     ClusterIP      192.168.1.1     <none>                                 443/TCP          718d
openshift      ExternalName   <none>          kubernetes.default.svc.cluster.local   <none>           718d
prom-service   NodePort       192.168.1.101   <none>                                 9090:32300/TCP   96m
prometheus     ClusterIP      192.168.1.221   <none>                                 9090/TCP         96m
```
In the resulting output, find the _graf-service_ service, and note the port that 3000 is bound to. In the above example, this is port 31034. This is the NodePort port. Now, open a web browser and browse to one of the IP addresses of a worker node (this is not the same as a Cluster-IP address and will not appear in the above output) at the NodePort port. For example: http://10.1.1.1:31034.
If everything is working correctly and you have network connectivity to the worker node and the NodePort port, you should now see the Grafana dashboard.
You can follow the same steps to access the Prometheus UI, which can be accessed over the bound port for the _prom-service_ NodePort service (32300 in the above example).

Notes:
As of this writing, this deployment has been tested on the following platforms:
- Azure Kubernetes Services (AKS)
- Google Kubernetes Engine (GKE)
- F5 Distributed Cloud vK8s (with some additional configuration - docs coming soon).
- RedHat OpenShift
- K3s

This collection was created by first leveraging [Kompose](https://kompose.io/) to generate the initial YAML files from the Application Study Tool Docker Compose file, followed by a series of changes needed to get it to work in a production-grade Kubernetes cluster. (More information on that coming soon.)
