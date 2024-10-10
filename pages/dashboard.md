# Dashboards

## Table of Contents
- [Fleet](#fleet-dashboards)
    - [Inventory](#inventory)
    - [Device Utilization](#device-utilization)
    - [Virtual Servers](#virtual-servers)
    - [SSL Certs](#ssl-certs)
- [Device](#device-dashboards)
    - [Overview](#overview)
    - [Top N](#top-n)
    - [Pools](#pools)
    - [Virtual Servers](#virtual-servers-1)
    - [iRules](#irules)
    - [WAF](.dashboard.)
- [Profile](#profile-dashboards)
    - [HTTP](#http)
- [Stats](#collector-stats)

## Accessing the dashboards

#### View The Dashboards
Once you have deployed the application, you can access the dashboards at `http://<hostname>:3000`, the default Grafana user/pass is `admin/admin`.

* Grafana Instance with pre-configured dashboards for quick insights at the device and "fleet" levels.

#### Changing the Grafana Credentials

You can update the Grafana user/pass by changing the values of 


### Fleet Dashboards

The fleet dashboards provide top level information of your environment

#### Inventory
![](./assets/BigIP-Fleet-Inventory.png)
*The inventory dashboard allows you to view the differences between BigIP devices in your inventory.*

#### Device Utilization
![](./assets/BigIP-Fleet-Device-Utilization.png)
*This dashboard provides a quick view on how much usage your box is receiving. To view more information about the device take a look at the [device overview dashboard](#overview).*

#### Virtual Servers
![](./assets/BigIP-Fleet-Virtual-Server.png)
*The Virtual Server dashboard provides an overview of all the virtual servers present in your inventory.*


#### SSL Certs
![](./assets/BigIP-Fleet-SSL-Certs.png)
*The SSL Certs view allows you to stay up to date on the status of your SSL certficates.*

### Device Dashboards

The device dashboards provide more grainular information about how the device is configured and how it is performing

#### Overview
![](./assets/BipIP-Device-Overview.png)
*This dashboard provides variety of metrics about the performance of the device.*
#### Top N
![](./assets/BigIP-Device-TopN.png)
*The Top N dashboard provides statistical highlights by presenting stats in a Top N, by default N is set to 10 this can be changed at top of the dashboard*
#### Pools
![](./assets/BigIP-Device-Pools.png)
*Here you can view*


#### Virtual Servers
![](./assets/BigIP-Device-Virtual-Server.png)
*Here you can view*

#### iRules
![](./assets/BigIP-Device-iRules.png)

#### WAF

![](./assets/BigIP-Device-WAF.png)




### Profile Dashboards

The profile dashboards dive into the different profiles configured on the devices and provide metrics about the traffic the profiles are receiving

#### HTTP

![](./assets/BigIP-Device:Profile-HTTP.png)
**


### Collector Stats

You can monitor how the collector is performing with the 

![](./assets/Collector-Stats.png)