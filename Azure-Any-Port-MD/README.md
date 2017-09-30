# Azure-Multi-IP_DEMO

[<img src="http://azuredeploy.net/deploybutton.png"/>](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fptglynn%2FPaloAltoNetworks%2Fmaster%2FAzure-Any-Port-MD%2FazureDeploy.json)

This template deploys a firewall sandwich environment that includes:

- One Public Load Balancer (LB-Public) - "Basic SKU"
- Two Palo Alto Networks Firewalls
- One Internal Load Balancer (LB-Web) - "Basic SKU"
- Two Ubuntu Servers for use as web servers
- One Egress Load Balancer (LB-Egress) - "Standard SKU"
- Multiple Subnets and UDRs to support the traffic flow

The template creates all the infrastructure and appropriate UDRs in the 10.0.0.0/16 VNET. Post-deployment tasks include:

- Licensing the FW
- Import the configurations "multi-ip-fw1" and "multi-ip-fw2" into the FW (default username is "paloalto" and default password is "Pal0Alt0@123")
- Installation/configuration of the web server software

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

The FW configurations provided in files multi-ip-fw1 and multi-ip-fw2 are designed to be used in a default deployment by updating the NAT rule with the public IP address of the LB-Public Load Balancer. Additional modifications may be required for use with a custom template deployment.
