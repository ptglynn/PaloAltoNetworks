#!/usr/bin/python

import json
import requests
import socket
import ssl
import time
import xml.etree.ElementTree as ElementTree

from oauth2client.client import GoogleCredentials
from googleapiclient import discovery
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from pprint import pprint
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Define various variables
# API Key to login to the FW
apiKey = "LUFRPT1CU0dMRHIrOWFET0JUNzNaTmRoYmkwdjBkWWM9alUvUjBFTTNEQm93Vmx0OVhFRlNkOXdJNmVwYWk5Zmw4bEs3NjgwMkh5QT0="
# Flag for verbose logging
debug = 1
# Host name of the local server. Must be defined but can be empty.
hostName = ""
# Port on local server on which to listen 
hostPort = 80
# List 1-999 that is used to determine the first available priority for rule creation
priority_list = range(1, 1000)
# List of rule priorities
rule_priorities = []

# Create the query that is sent to the FW to retrieve the XFF from the URLF log
fw_url_log_cmd1 = "https://"
fw_url_log_cmd2 = "/api/?type=log&log-type=url&key="+apiKey+"&query=((sessionid%20eq%20'"
fw_url_log_cmd3 = "')%20and%20(natsport%20eq%20'"
fw_url_log_cmd4 = "')%20and%20(receive_time%20geq%20'"
fw_url_log_cmd5 = "'))"

# Create the query that is used to determine when the log query has completed
fw_url_xff_cmd1 = "https://"
fw_url_xff_cmd2 = "/api/?type=log&action=get&key="+apiKey+"&job-id="

# Query to retrieve the project ID associated with the FW
get_project_cmd = "http://metadata.google.internal/computeMetadata/v1/project/project-id"

"""
Query the FW for the URLF log associated with the original threat
"""
def url_log_jobid_extracter(sessionid, natsport, rxtime, client_address):
  # Create the command to query the FW
  cmd = fw_url_log_cmd1+str(client_address)+fw_url_log_cmd2+str(sessionid)+fw_url_log_cmd3+str(natsport)+fw_url_log_cmd4+rxtime.split(" ")[0]+"%20"+rxtime.split(" ")[1]+fw_url_log_cmd5
  if debug:
    print( "The command to extract jobid is", cmd )
  # Send query to the FW
  log_query = requests.get(cmd, verify=False)
  response = log_query.text
  if debug:
    print( "response = ", response )
  dom = ElementTree.fromstring(response)
  # Extract the jobid from the FW and return it
  jobid = dom[0].find('job').text
  return jobid

"""
Extract the XFF
"""
def xff_extractor(jobid, client_address):
  # Create the command to query the FW by jobid
  # The original query does not return immediately so we query multiple times (up to 6 @ 2 scond intervals) for the results.
  cmd = fw_url_xff_cmd1+str(client_address)+fw_url_xff_cmd2+str(jobid)
  if debug:
    print( "The command to extract XFF is", cmd )
  # Send query to the FW
  xff_query = requests.get(cmd, verify=False)
  response = xff_query.text
  if debug:
    print( "response = ", response )
  dom = ElementTree.fromstring(response)
  # If we do not get a positive response, then we trigger a retry 
  if dom[0][1][0].attrib['count'] == "0":
      return "RETRY"
  else:
      # Otherwise, return the IP of the bad actor
      xff = dom.find('./result/log/logs/entry/xff').text
      return xff

"""
Get the project ID
"""
def get_project_id():
  # Create the command to query the GCP environment for the project ID
  cmd = get_project_cmd
  # Send query to GCP
  get_project = requests.get(cmd, headers={'Metadata-Flavor':'Google'})
  project_id = get_project.text
  if debug:
    print( "project_id = ", project_id )
  # Return the project ID to the requester
  return project_id

"""
Get a list of all currently-used rule priorities
"""
def get_rule_priorities(service, project_id, policy_name):
  if debug:
    print( "service = ",service )
    print( "project_id = ", project_id )
    print( "policy_name = ", policy_name )
  # Create a filter so that we only grab the rules associated with the target policy
  policy_filter = "name eq "+policy_name
  request = service.securityPolicies().list(project=project_id, filter=policy_filter)
  # Send query to GCP
  response = request.execute()
  # Iterate through the response and build a list of extant rule priorities
  for item in response['items'][0]['rules']:
    if debug:
      print( "priority = ", item['priority'] )
    rule_priorities.append(item['priority'])
    rule_priorities.sort(key=int)
  # Return the list of list of extant rule priorities
  return rule_priorities

"""
Get next available rule priority
"""
def get_next_priority(list_priorities, priority_list):
  if debug:
    print( "list_priorities = ",list_priorities )
    print( "priority_list = ", priority_list )
  # Compare the list of extant rule priorities to the reference list
  list_diff = list(set(priority_list) - set(list_priorities))
  # Sort the list numerically
  list_diff.sort(key=int)
  # Grab the first available number
  next_priority = list_diff[0]
  # Return the first available number (priority) to the requester
  return next_priority

"""
Block the bad actor
"""
def create_security_rule(service, project_id, policy_name, next_available_priority, actual_xff):
  if debug:
    print( "service = ",service )
    print( "project_id = ",project_id )
    print( "policy_name = ",policy_name )
    print( "next_available_priority = ",next_available_priority )
    print( "actual_xff = ", actual_xff )
  # Create the description for the security rule
  rule_description = "block "+actual_xff
  # Create the source match for the host we wish to block
  rule_source = actual_xff+"/32"
  # Create the json-formatted request body
  security_policy_body = {
    "description": rule_description,
    "priority": next_available_priority,
    "match": {
      "versionedExpr": "SRC_IPS_V1",
      "config": {
        "srcIpRanges": [
          rule_source
        ]
      }
    },
    "action": "deny(403)",
    "preview": False,
  }
  if debug:
    print( "security_policy_body = ", security_policy_body )
  # Send the properly-formatted request to GCP
  request = service.securityPolicies().addRule(project=project_id, securityPolicy=policy_name, body=security_policy_body)
  response = request.execute()
  # Return the response
  return response

class MyServer(BaseHTTPRequestHandler):

  """
  Process the POSTed data from the FW
  """
  def do_POST(self):
    if debug:
      print( "incoming http: ", self.path )
    # Get the size of data posted
    content_length = int(self.headers['Content-Length'])
    # Get the actual data from the post
    post_data = self.rfile.read(content_length)
    # Get the address of the firewall that sent the request
    client_address = self.client_address[0]
    # Parse the request for the relevant information: Session-ID, NAT Source Port, Log Receipt Time, and FW Security Policy Name
    json_data = json.loads(post_data.decode('utf-8'))
    sessionid = json_data['SessionID']
    natsport = json_data['NATSRCPort']
    rxtime = json_data['ReceiveTime']
    policy_name = json_data['SecurityPolicy']

    if debug:
        print( "post_data = ", post_data )
        print( "client_address = ", client_address )
        print( "json_data = ", json_data )
        print( "sessionid = ", sessionid )
        print( "natsport = ", natsport )
        print( "rxtime = ", rxtime )
    
    self.send_response(200)

    self.connection.close()
    
    # Try 6 times to gather the original client IP associated with the threat.
    # The FW query is no synchronous so we make a callback to get the results.
    count = 0
    while count < 5:
      # Job ID associated with the query for the URLF with the XFF information
      jobid = url_log_jobid_extracter(sessionid, natsport, rxtime, client_address)
      if debug:
        print('Job id is:', jobid)
        print("Sleeping for 2 seconds...")
      time.sleep(3)
      # Query the FW and get back the XFF information or "RETRY" if we need to check back
      xff = xff_extractor(jobid, client_address)
      if xff == "RETRY":
        count += 1
      else:
        count = 6
        if debug:
          print( "Original XFF extracted is", xff )
        actual_xff = xff.split(",")[0]
        if debug:
          print( "Actual XFF extracted is", actual_xff )
    
    """
    Get project ID so we know which project's security policy we are updating
    """
    project_id = get_project_id()
    if debug:
      print( "project id is ", project_id )

    """
    Get a list of all currently-used rule priorities
    """
    list_priorities = get_rule_priorities(service, project_id, policy_name)
    if debug:
      print( "priorities in use = ", list_priorities )

    """
    Get next available rule priority
    """
    next_available_priority = get_next_priority(list_priorities, priority_list)
    if debug:
      print( "next_available_priority = ",next_available_priority )

    """
    Block the bad actor
    """
    create_rule = create_security_rule(service, project_id, policy_name, next_available_priority, actual_xff)
    if debug:
      print( "security rule created. response = ",create_rule )

# Start listening for HTTP POSTs from the FW
myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))
# Get the credentials from the GCP environment so that we can query/modify as required
credentials = GoogleCredentials.get_application_default()
service = discovery.build('compute', 'beta', credentials=credentials)

# Run as a server in a continuous loop until keyboard interrupt received
try:
  myServer.serve_forever()
except KeyboardInterrupt:
  pass

# If we recieve an interrupt, exit gracefully
myServer.server_close()
if debug:
  print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
