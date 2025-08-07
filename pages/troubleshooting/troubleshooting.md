---
layout: page
title: Troubleshooting
nav_order: 4
has_children: true
permalink: /troubleshooting
---

# Troubleshooting AST

1. TOC
{:toc}

## Increase REST memory and timeouts to improve Big-IP REST experience
Per [AS3 Best Practices guide](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/userguide/best-practices.html#increase-timeout-values-if-the-rest-api-is-timing-out)   

Increase internal timeouts from 60 to 600 seconds:
```
tmsh modify sys db icrd.timeout value 600
tmsh modify sys db restjavad.timeout value 600
tmsh modify sys db restnoded.timeout value 600
```

Increase RESTJAVAD memory (skip if experiencing memory pressure):
```
tmsh modify sys db provision.extramb value 2048
tmsh modify sys db provision.tomcat.extramb value 256
```

Applies to TMOS 15.1.9 +:  
```
tmsh modify sys db provision.restjavad.extramb value 600
```  

save configuration:
```
tmsh save sys config
```
verify everything looks good:
```
tmsh list sys db icrd.timeout
tmsh list sys db restjavad.timeout  
tmsh list sys db restnoded.timeout 
tmsh list sys db provision.extramb
tmsh list sys db provision.tomcat.extramb
tmsh list sys db provision.restjavad.extramb
```

then restart services:
```
tmsh restart sys service restjavad
tmsh restart sys service restnoded
```
## Optimize REST Guidance and further examples
> See the Repo located here [Megamattzilla](https://github.com/megamattzilla/as3-tips-and-tricks?tab=readme-ov-file#1-increase-rest-memory-and-timeouts-to-improve-big-ip-rest-experience-) for further information.
___

## Useful Commands

### View Docker Container Status
You can view the state of the docker containers after they've been started with `docker ps`.
The STATUS field is a good indicator whether containers are running correctly or not.

This output shows everything looks good:
```shell
$ docker ps
CONTAINER ID   IMAGE                                                                      COMMAND                  CREATED              STATUS          PORTS                       NAMES
cb4cf8867390   grafana/grafana:11.6.3                                                     "/run.sh"                About a minute ago   Up 49 seconds   0.0.0.0:3000->3000/tcp      grafana
bb8891f2cd47   prom/prometheus:v2.53.5                                                    "/bin/prometheus --c…"   About a minute ago   Up 49 seconds   0.0.0.0:9090->9090/tcp      prometheus
df2739cd67cb   ghcr.io/f5devcentral/application-study-tool/otel_custom_collector:v0.6.0       "/otelcol-custom --c…"   About a minute ago   Up 49 seconds   4317/tcp, 55679-55680/tcp   application-study-tool-otel-collector-1
```

This output shows a problem (Restarting container) for the `application-study-tool-otel-collector-1`
container (the otel collector):
```shell
$ docker ps
CONTAINER ID   IMAGE                                                                      COMMAND                  CREATED          STATUS                         PORTS                    NAMES
fdbde8a3ee16   ghcr.io/f5devcentral/application-study-tool/otel_custom_collector:v2.0.1       "/otelcol-custom --c…"   14 seconds ago   Restarting (1) 5 seconds ago                            application-study-tool-otel-collector-1
b7ef41accd46   grafana/grafana:11.6.3                                                     "/run.sh"                14 seconds ago   Up 13 seconds                  0.0.0.0:3000->3000/tcp   grafana
8edff3e8666e   prom/prometheus:v2.53.5                                                    "/bin/prometheus --c…"   14 seconds ago   Up 13 seconds                  0.0.0.0:9090->9090/tcp   prometheus
```

### View Docker Container Logs
When containers aren't running correctly or other issues are present, the container logs are a good place
to look. Once you have the Container ID or Container Name field from the output of `docker ps`, you can
view the container logs using the `docker logs <container id or name>` command.

Logs for the broken container above (which show a parsing error with the config file)
can be gathered as shown:

```shell
$ docker logs application-study-tool-otel-collector-1
Error: failed to get config: cannot unmarshal the configuration: decoding failed due to the following error(s):

'receivers' expected a map, got 'string'
2024/10/17 15:53:44 collector server run finished with error: failed to get config: cannot unmarshal the configuration: decoding failed due to the following error(s):

'receivers' expected a map, got 'string'
```

### Save Logs To A File
The output of `docker logs` command for specific containers may be requested during troubleshooting.
The logs can be gathered and saved to file with a command similar to:

```shell
$ docker logs application-study-tool-otel-collector-1 >& otellogs.txt && gzip otellogs.txt
```

### Stop and Start A Container
Individual containers can be started and stopped using the `docker stop <container name or id>` command.
This will cause the container to restart with any modifications to config files picked up (alternative
to the `docker compose down` and `docker compose up` commands which restart all containers):

```shell
$ docker stop fdbde8a3ee16
fdbde8a3ee16

$ docker start fdbde8a3ee16
fdbde8a3ee16
```

## Grafana Not Reachable
Once containers are up and running, you should be able to view the Grafana instance by navigating to port
`3000` on the host machine. If this isn't working, things to check include:

* Run `docker ps` and check the status of the Grafana container.
* Ensure port `3000` is open between the client browser and the instance running AST.
* Check grafana logs with `docker logs -f grafana`
* Check if the prometheus endpoint (avaialble on port `9090` of the AST instance) is reachable (as a
 second data point assuming none of the above show issues).


## Dashboard Data Not Visible (All Dashboards)
If Grafana is loading but dashboard data is not populating in any dashboards, there are a few things to
check:

### Check the Opentelemetry Collector Dashboard
The opentelemetry collector dashboard at the top level of the 'Dashboards' list in Grafana is a good
starting point. The data in this dashboard is collected through a different mechanism from the rest of
the dashboards.

* If data is present in this dashboard (but no others), it indicates an issue with the collection of data
from the BigIPs.
* If no data is present in this dashboard, it indicates a problem with the connection between Prometheus
and Grafana.

**If Data Is Present**

If data is present here, there's very likely an issue with collection from the BigIPs themselves.
Things to check:

* Is the Otel Collector container running correctly (`docker ps`)
* Do the otel collector container logs show any
    1. Authentication errors:
        * `2024-10-17T16:23:50.658Z	error	scraperhelper/scrapercontroller.go:197	Error scraping metrics	{"kind": "receiver", "name": "bigip/1", "data_type": "metrics", "error": "endpoint /mgmt/shared/authn/login returned code 401", "scraper": "bigip"}`
    2. Network connection problems:
        * `2024-10-17T16:17:44.347Z        error   scraperhelper/scrapercontroller.go:197  Error scraping metrics  {"kind": "receiver", "name": "bigip/1", "data_type": "metrics", "error": "failed to make http request: Post \"https://10.0.0.1/mgmt/shared/authn/login\": net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)", "scraper": "bigip"}`
* Do the `Metrics Points Receive Rate` and `Metrics Points Export Rate` in the dashboard show failures
or '0' (indicating nothing is being collected)? 

**If Data Is NOT Present**

This indicates that there is an issue with the communication between Grafana and Prometheus.
Check:
* Is the prometheus container running `docker ps`
* Are there any error logs present in the prometheus container (if running or not) `docker logs prometheus`
* Can you reach the prometheus interface on port `9090` of the AST host (assuming firewalls are open)

## Dashboard Data Not Visible (Specific Dashboards)

If the dashboards are GTM or DNS profile dashboards, see below.

For other dashboards, ensure that:
* The dashboard 'time range' in the upper right is set to a window where data is expected to exist.
* Any device, virtual server, or other selectors in the upper left are set to valid values where data
should exist.
* Check the responses for a specific broken panel by clicking the '3 dot icon' (upper right while 
hovering) and selecting 'Inspect > Query'
* Are any queries to the BigIP timing or erroring out? Check the otel collector logs (`docker ps`) and
the 'BigIP Collector Stats' dashboard at the top level of the Dashboards section in Grafana 

## GTM, DNS, ASM, APM, Firewall, NAT Metrics Not Loading

Metrics for GTM, DNS, ASM, APM, Firewall, NAT are disabled by default. See 
[Configuration > Configuration Helper (Recommended) > Configure DNS & GTM]({{ site.url }}{{ site.baseurl }}/config/config_helper/config_dns_gtm.html) for instructions to enable.

## Max API Tokens Reached For User

Several BigIP Bugs have been identified which can result in maximum tokens issued errors:

* [ID1787517](https://cdn.f5.com/product/bugtracker/ID1787517.html)
* [ID1103369](https://cdn.f5.com/product/bugtracker/ID1103369.html)

v0.9.0 should prevent issues in ID1787517 from occuring on most systems. ID1103369 includes workaround steps for user encountering that issue.
