---
layout: page
title: Via env File
parent: Secrets Management
grandparent: Configuration
nav_order: 1
---

## Configure Device Secrets Via File

The application study tool default configuration relies on environment variables
which contain device access credentials. There are a number of ways to manage and
inject secrets into a container environment (modifications to the docker-compose file
to support your preferred management process are encouraged), but for simplicity,
if there is a file named .env.device-secrets in the root project directory they will be
mounted.

Create a file called .env.device-secrets, and add your BIP passwords like so:
```
BIGIP_PASSWORD_1=foo-bar123!
BIGIP_PASSWORD_2=bar-foo123!
```

The variable name (the part on the left of the equal sign) must match the configured
value for the devices that use this password in config/ast_defaults.yaml or device specifc
cofig in config/bigip_receivers.yaml. In the following example, bigip/1 uses BIGIP_PASSWORD_1
from  the defaults and bigip/2 uses BIGIP_PASSWORD_2 from the device settings:

```
##############################
## config/ast_defaults.yaml 
##############################

bigip_receiver_defaults:
  ...
  password: "${env:BIGIP_PASSWORD_1}"
  ...

##############################
## config/bigip_receivers.yaml
##############################

# This gets the default "${env:BIGIP_PASSWORD_1}"
bigip/1:
  endpoint: https://10.0.0.1

# This overrides it with "${env:BIGIP_PASSWORD_2}"
bigip/2:
  endpoint: https://10.0.0.1
  password: ${env:BIGIP_PASSWORD_2}

```