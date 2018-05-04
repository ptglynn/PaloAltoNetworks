# Copyright 2016 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Creates the network."""

COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'

def GenerateConfig(context):
  """Creates the network."""

  resources = [{
      'name': 'management',
      'type': 'compute.v1.network',
      'properties': {
          'autoCreateSubnetworks': False
      }
  },{
      'name': 'untrust',
      'type': 'compute.v1.network',
      'properties': {
          'autoCreateSubnetworks': False
      }
  },{
      'name': 'trust',
      'type': 'compute.v1.network',
      'properties': {
          'autoCreateSubnetworks': False
      }
  },{
      'name': 'management-subnet',
      'type': 'compute.v1.subnetwork',
      'properties': {
          'region': context.properties['region'], 
          'network': '$(ref.management.selfLink)',
          'ipCidrRange': '10.5.0.0/24'
      }
  },{
      'name': 'untrust-subnet',
      'type': 'compute.v1.subnetwork',
      'properties': {
          'region': context.properties['region'], 
          'network': '$(ref.untrust.selfLink)',
          'ipCidrRange': '10.5.1.0/24'
      }
  },{
      'name': 'trust-subnet',
      'type': 'compute.v1.subnetwork',
      'properties': {
          'region': context.properties['region'], 
          'network': '$(ref.trust.selfLink)',
          'ipCidrRange': '10.5.2.0/24'
      }
  },{
      'name': 'management-firewall',
      'type': 'compute.v1.firewall',
      'properties': {
          'region': context.properties['region'], 
          'network': '$(ref.management.selfLink)',
          'direction': 'INGRESS',
          'priority': 1000,
          'sourceRanges': ['0.0.0.0/0'],
          'allowed': [{
            'IPProtocol': 'tcp',
            'ports': [22, 443]
          }]
      }
  },{
      'name': 'untrust-firewall',
      'type': 'compute.v1.firewall',
      'properties': {
          'region': context.properties['region'], 
          'network': '$(ref.untrust.selfLink)',
          'direction': 'INGRESS',
          'priority': 1000,
          'sourceRanges': ['0.0.0.0/0'],
          'allowed': [{
            'IPProtocol': 'tcp',
            'ports': [80, 221, 222]
          }]
      }
  },{
      'name': 'trust-firewall',
      'type': 'compute.v1.firewall',
      'properties': {
          'region': context.properties['region'], 
          'network': '$(ref.trust.selfLink)',
          'direction': 'INGRESS',
          'priority': 1000,
          'sourceRanges': ['0.0.0.0/0'],
          'allowed': [{
            'IPProtocol': 'tcp',
            },{
            'IPProtocol': 'udp',
            },{
            'IPProtocol': 'icmp'
          }]
      }
  },{
        'name': 'firewalla-instancetemplate',
        'type': 'compute.v1.instanceTemplate',
        'properties': {
            'properties': {
                'machineType': 'n1-standard-4',
                'canIpForward': True,
                'networkInterfaces': [{
                    'network': '$(ref.untrust.selfLink)',
                    'subnetwork': '$(ref.untrust-subnet.selfLink)',
                    'networkIP': '10.5.1.2',
                    'accessConfigs': [{
                        'name': 'ext access',
                        'type': 'ONE_TO_ONE_NAT'
                        }]
                    },{
                    'network': '$(ref.management.selfLink)',
                    'subnetwork': '$(ref.management-subnet.selfLink)',
                    'networkIP': '10.5.0.2',
                    'accessConfigs': [{
                        'name': 'mgmt access',
                        'type': 'ONE_TO_ONE_NAT'
                        }]
                    },{
                    'network': '$(ref.trust.selfLink)',
                    'subnetwork': '$(ref.trust-subnet.selfLink)',
                    'networkIP': '10.5.2.2',
                }],
                'disks': [{
                    'type': 'PERSISTENT',
                    'deviceName': 'boot',
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': context.properties['fwsourceimage'],
                    }
                }],
                'metadata': {
                    'items': [{
                        'key': 'vmseries-bootstrap-gce-storagebucket',
                        'value': context.properties['bootstrapbucket']
                    },{
                        'key': 'ssh-keys',
                        'value': context.properties['sshkey']
                    },{
                        'key': 'serial-port-enable',
                        'value': 'true' 
                    }]
                },
                'serviceAccounts': [{
                    'email': 'default',
                    'scopes': [
                          'https://www.googleapis.com/auth/cloud.useraccounts.readonly',
                          'https://www.googleapis.com/auth/devstorage.read_only',
                          'https://www.googleapis.com/auth/logging.write',
                          'https://www.googleapis.com/auth/monitoring.write',
                    ]}
                ],
                'minCpuPlatform': 'Intel Skylake'
            }
        }
    },{
        'name': 'firewallb-instancetemplate',
        'type': 'compute.v1.instanceTemplate',
        'properties': {
            'properties': {
                'machineType': 'n1-standard-4',
                'canIpForward': True,
                'networkInterfaces': [{
                    'network': '$(ref.untrust.selfLink)',
                    'subnetwork': '$(ref.untrust-subnet.selfLink)',
                    'networkIP': '10.5.1.3',
                    'accessConfigs': [{
                        'name': 'ext access',
                        'type': 'ONE_TO_ONE_NAT'
                        }]
                    },{
                    'network': '$(ref.management.selfLink)',
                    'subnetwork': '$(ref.management-subnet.selfLink)',
                    'networkIP': '10.5.0.3',
                    'accessConfigs': [{
                        'name': 'mgmt access',
                        'type': 'ONE_TO_ONE_NAT'
                        }]
                    },{
                    'network': '$(ref.trust.selfLink)',
                    'subnetwork': '$(ref.trust-subnet.selfLink)',
                    'networkIP': '10.5.2.3',
                }],
                'disks': [{
                    'type': 'PERSISTENT',
                    'deviceName': 'boot',
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': context.properties['fwsourceimage'],
                    }
                }],
                'metadata': {
                    'items': [{
                        'key': 'vmseries-bootstrap-gce-storagebucket',
                        'value': context.properties['bootstrapbucket']
                    },{
                        'key': 'ssh-keys',
                        'value': context.properties['sshkey']
                    },{
                        'key': 'serial-port-enable',
                        'value': 'true' 
                    }]
                },
                'serviceAccounts': [{
                    'email': 'default',
                    'scopes': [
                          'https://www.googleapis.com/auth/cloud.useraccounts.readonly',
                          'https://www.googleapis.com/auth/devstorage.read_only',
                          'https://www.googleapis.com/auth/logging.write',
                          'https://www.googleapis.com/auth/monitoring.write',
                    ]}
                ],
                'minCpuPlatform': 'Intel Skylake'
            }
        }
    },{
        'name': 'webservera-instancetemplate',
        'type': 'compute.v1.instanceTemplate',
        'properties': {
            'properties': {
                'machineType': 'n1-standard-1',
                'networkInterfaces': [{
                    'network': '$(ref.trust.selfLink)',
                    'subnetwork': '$(ref.trust-subnet.selfLink)',
                    'networkIP': '10.5.2.4',
                }],
                'disks': [{
                    'type': 'PERSISTENT',
                    'deviceName': 'boot',
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': context.properties['hostsourceimage'],
                    }
                }],
                'metadata': {
                    'items': [{
                        'key': 'ssh-keys',
                        'value': context.properties['sshkey']
                    },{
                        'key': 'serial-port-enable',
                        'value': 'true' 
                    }]
                },
                'serviceAccounts': [{
                    'email': 'default',
                    'scopes': [
                          'https://www.googleapis.com/auth/cloud.useraccounts.readonly',
                          'https://www.googleapis.com/auth/devstorage.read_only',
                          'https://www.googleapis.com/auth/logging.write',
                          'https://www.googleapis.com/auth/monitoring.write',
                    ]}
                ],
                'minCpuPlatform': 'Intel Skylake'
            }
        }
    },{
        'name': 'webserverb-instancetemplate',
        'type': 'compute.v1.instanceTemplate',
        'properties': {
            'properties': {
                'machineType': 'n1-standard-1',
                'networkInterfaces': [{
                    'network': '$(ref.trust.selfLink)',
                    'subnetwork': '$(ref.trust-subnet.selfLink)',
                    'networkIP': '10.5.2.5',
                }],
                'disks': [{
                    'type': 'PERSISTENT',
                    'deviceName': 'boot',
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': context.properties['hostsourceimage'],
                    }
                }],
                'metadata': {
                    'items': [{
                        'key': 'ssh-keys',
                        'value': context.properties['sshkey']
                    },{
                        'key': 'serial-port-enable',
                        'value': 'true' 
                    }]
                },
                'serviceAccounts': [{
                    'email': 'default',
                    'scopes': [
                          'https://www.googleapis.com/auth/cloud.useraccounts.readonly',
                          'https://www.googleapis.com/auth/devstorage.read_only',
                          'https://www.googleapis.com/auth/logging.write',
                          'https://www.googleapis.com/auth/monitoring.write',
                    ]}
                ],
                'minCpuPlatform': 'Intel Skylake'
            }
        }
    },{
        'name': 'firewall-healthcheck',
        'type': 'compute.v1.healthCheck',
        'properties': {
            'timeoutSec': 3,
            'checkIntervalSec': 3,
            'unhealthyThreshold': 5,
            'healthyThreshold': 2,
            'type': 'HTTP',
            'httpHealthCheck': {
                'port': 80,
                'requestPath': '/'
            }
        }
       },{
        'name': 'webserver-healthcheck',
        'type': 'compute.v1.healthCheck',
        'properties': {
            'timeoutSec': 3,
            'checkIntervalSec': 3,
            'unhealthyThreshold': 5,
            'healthyThreshold': 2,
            'type': 'HTTP',
            'httpHealthCheck': {
                'port': 80,
                'requestPath': '/'
            }
        }
       },{
        'name': 'firewalla-instancegroup',
        'type': 'compute.v1.instanceGroupManager',
        'properties': {
            'zone': context.properties['zone'],
            'targetSize': 1,
            'baseInstanceName': 'firewalla',
            'instanceTemplate': '$(ref.firewalla-instancetemplate.selfLink)'
        }
      },{
        'name': 'firewallb-instancegroup',
        'type': 'compute.v1.instanceGroupManager',
        'properties': {
            'zone': context.properties['zone'],
            'targetSize': 1,
            'baseInstanceName': 'firewallb',
            'instanceTemplate': '$(ref.firewallb-instancetemplate.selfLink)'
        }
      },{
        'name': 'webservera-instancegroup',
        'type': 'compute.v1.instanceGroupManager',
        'properties': {
            'zone': context.properties['zone'],
            'targetSize': 1,
            'baseInstanceName': 'webservera',
            'instanceTemplate': '$(ref.webservera-instancetemplate.selfLink)'
        }
      },{
        'name': 'webserverb-instancegroup',
        'type': 'compute.v1.instanceGroupManager',
        'properties': {
            'zone': context.properties['zone'],
            'targetSize': 1,
            'baseInstanceName': 'webserverb',
            'instanceTemplate': '$(ref.webserverb-instancetemplate.selfLink)'
        }
      },{
        'name': 'firewall-backendservice',
        'type': 'compute.v1.backendService',
        'properties': {
            'healthChecks': [ '$(ref.firewall-healthcheck.selfLink)' ],
            'port': 80,
            'portName': 'http',
            'protocol': 'HTTP',
            'timeoutSec': 30,
            'backends': [ { 'group': '$(ref.firewalla-instancegroup.instanceGroup)' },
                          { 'group': '$(ref.firewallb-instancegroup.instanceGroup)' }
            ]
        }
      },{
        'name': 'webserver-regionbackendservice',
        'type': 'compute.v1.regionBackendService',
        'properties': {
            'zone': context.properties['zone'],
            'region': context.properties['region'],
            'loadBalancingScheme': 'INTERNAL',
            'healthChecks': [ '$(ref.webserver-healthcheck.selfLink)' ],
            'protocol': 'TCP',
            'timeoutSec': 30,
            'backends': [ { 'group': '$(ref.webservera-instancegroup.instanceGroup)' },
                          { 'group': '$(ref.webserverb-instancegroup.instanceGroup)' }
             ]
        }
      },{
        'name': 'firewall-urlmap',
        'type': 'compute.v1.urlMap',
        'properties': {
            'defaultService': '$(ref.firewall-backendservice.selfLink)'
        }
      },{
        'name': 'firewall-httpproxy',
        'type': 'compute.v1.targetHttpProxy',
        'properties': {
            'urlMap': '$(ref.firewall-urlmap.selfLink)'
        }
      },{
        'name': 'firewall-globalforwardingrule',
        'type': 'compute.v1.globalForwardingRule',
        'properties': {
            'loadBalancingScheme': 'EXTERNAL',
            'IPProtocol': 'TCP',
            'portRange': 80,
            'region': context.properties['region'],
            'target': '$(ref.firewall-httpproxy.selfLink)'
        }
      },{
        'name': 'webserver-forwardingrule',
        'type': 'compute.v1.forwardingRule',
        'properties': {
            'region': context.properties['region'],
            'network': '$(ref.trust.selfLink)',
            'subnetwork': '$(ref.trust-subnet.selfLink)',
            'IPAddress': '10.5.2.7',
            'loadBalancingScheme': 'INTERNAL',
            'IPProtocol': 'TCP',
            'ports': [ 80 ],
            'backendService': '$(ref.webserver-regionbackendservice.selfLink)'
        }
      }]
  return {'resources': resources}
