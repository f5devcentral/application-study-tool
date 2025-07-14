# Application Study Tool Configuration Wizard

This script is a user-friendly way to easily and quickly configure the Application Study Tool for its initial deployment.
Upon running it, it will ask you a series of questions, including BIG-IP management IP addresses, usernames, passwords,
and other required settings, and use this information to create and update the required config files in AST.
Once it completes, AST is ready to be run. It also gives you the option of running AST right from the script.

Note: This script is meant to be run only at initial installation time.
If you need to make changes afterwards or you make an error while inputting the required values,
you will need to re-run the script and re-enter all of your settings.
Alternatively, to just make one-off edits, you can manually edit the config files after the script exits.

## Prerequisites
Pre-installing Docker or Podman prior to running this script is recommended
in order to allow this script to launch the Application Study Tool. However, it is not strictly required.

If not already done, the following steps are requirements for running this script.
```
$ git clone https://github.com/f5devcentral/application-study-tool.git
$ cd application-study-tool
$ chmod +x config-wizard.sh
$ ./config-wizard.sh
```

## How to Use This Tool
This script will prompt you for the information it needs to configure the Application Study Tool.
This includes BIG-IP management IP addresses, credentials, and other information. It will continue adding BIG-IP devices
until you tell it to stop (by just hitting ENTER instead of entering a management IP address).

It updates the required configuration files as it goes, so if you abort the script in the middle of using it,
your the configuration information you have entered thus far will be saved in the AST configuration files. You will then
want to revisit this process by manually editing the configuration files and adding any remaining settings.
