# Azure-Any-Port-Budapest-Demo

[<img src="http://azuredeploy.net/deploybutton.png"/>](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fptglynn%2FPaloAltoNetworks%2Fmaster%2FAzure-Any-Port-MD-Budapest%2FazureDeploy.json)

IMPORTANT: This template was designed to be used with Palo Alto Networks PANOS-8.1 as well as the Azure Standard Load Balancer. Both are in preview/beta mode. Please contact your Palo Alto Networks field team to gain access to PANOS 8.1 beta. For the Standard Load Balancer Preview, refer to the following:

https://docs.microsoft.com/en-us/azure/load-balancer/load-balancer-standard-overview#preview-sign-up

The template is configured to bootstrap the firewalls and use the file bootstrap.xml may be used as the configuration file for both devices. Please refer to the PANOS 8.1 New Features Guide for information on creating a bootstrap package for use with this template.

This template deploys a firewall sandwich environment that includes:

- One Public Load Balancer (LB-Public) - "Basic SKU"
- Two Palo Alto Networks Firewalls
- One Internal Load Balancer (LB-Web) - "Basic SKU"
- Two Ubuntu Servers for use as web servers
- One Egress Load Balancer (LB-Egress) - "Standard SKU"
- Multiple Subnets and UDRs to support the traffic flow

The template creates all the infrastructure and appropriate UDRs in the 10.0.0.0/16 VNET. 

The post-deployment are:

- License the FW (if not done as part of the bootstrap process)
- Install/configure the web server software

NOTE: default username is "paloalto" and default password is "Pal0Alt0@123"

To Deploy ARM Template using Azure CLI in ARM mode

- Download the two JSON files: azureDeploy.json and azureDeploy.parameters.json
- Customize the azureDeploy.parameters.json file and then deploy it from your computer.
- Install the latest Azure CLI for your computer.
- Validate and deploy the ARM template:
    azure login
    azure config mode arm
    azure  group  template  validate  -g YourResourceGroupName \
        -e  azureDeploy.json   -f  azureDeploy.parameters.json
    azure group create -v -n YourResourceGroupName -l YourAzureRegion  \
        -d  YourDeploymentLabel  -f azureDeploy.json -e azureDeploy.parameters.json

To check the status of your deployment:

- Via CLI: azure vm show -g YourResourceGroupName -n YourDeploymentLabel
- Via Azure Portal: Your Resource Group > Deployment or Alert Logs

The bootstrap.xml file designed to be used in a default deployment. Additional modifications may be required for use with a custom template deployment.
