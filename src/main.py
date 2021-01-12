"""
Using Audit Logs, creates new DNS entries on the presence of new VMs
"""
from googleapiclient.discovery import build
import base64
import json
import os
import re
import logging

PROJECT = os.environ.get('CLOUD_DNS_PROJECT')
ZONE = os.environ.get('CLOUD_DNS_ZONE')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

compute = build('compute', 'v1', cache_discovery=False)
dns = build('dns', 'v1beta2', cache_discovery=False)


def create(event, context):
  if 'data' in event:
    event = json.loads(base64.b64decode(event['data']).decode('utf-8'))
  print('Event: ' + str(event))
  print('Context: ' + str(context))
  instance = Instance(event['protoPayload']['resourceName'])
  zone = DNS(ZONE)
  record_name = construct_record_name(instance.instance_name, instance.zone,
                                      zone.dns_name)
  record_set = construct_record_set('A', record_name, instance.internal_ip())
  create_record(zone, [record_set])


def delete(event, context):
  if 'data' in event:
    event = json.loads(base64.b64decode(event['data']).decode('utf-8'))
  print('Event: ' + str(event))
  print('Context: ' + str(context))
  instance = Instance(event['protoPayload']['resourceName'])
  zone = DNS(ZONE)
  record_name = construct_record_name(instance.instance_name, instance.zone,
                                      zone.dns_name)
  record_set = zone.get_record_set(record_name)
  delete_record(zone, [record_set])


def construct_record_name(name, zone, dns_name):
  return f'{name}.{zone}.{dns_name}'


def create_record(zone, record_sets):
  zone.update_record_sets(additions=record_sets, deletions=[])


def delete_record(zone, record_sets):
  zone.update_record_sets(additions=[], deletions=record_sets)


def construct_record_set(record_type, record_name, ip_address):
  return {
      'kind': 'dns#resourceRecordSet',
      'name': record_name,
      'rrdatas': [ip_address],
      'ttl': 86400,
      'type': record_type
  }


class DNS:
  """
  Get DNS API stuff
  """

  def __init__(self, zone_name):
    self.zone = self.get_dns_zone(zone_name)
    self.zone_name = self.zone['name']
    self.dns_name = self.zone['dnsName']

  def get_dns_zone(self, zone_name):
    try:
      request = dns.managedZones().get(project=PROJECT, managedZone=zone_name)
      response = request.execute()
      return response
    except Exception as e:  # pylint: disable=broad-except
      logger.exception(
          'Cloud DNS Project or Managed Zone not valid, DNS record not created: %s',
          e)

  def get_record_set(self, record_name):
    try:
      # Iterate through until there's a GET method available
      request = dns.resourceRecordSets().list(project=PROJECT,
                                              managedZone=self.zone_name)
      response = request.execute()
      for recordset in response['rrsets']:
        if record_name == recordset['name']:
          return recordset
    except Exception as e:  # pylint: disable=broad-except
      logger.exception(e)
      logger.exception('No recordsets matching %s in zone', record_name)

  def update_record_sets(self, additions=None, deletions=None):
    try:
      request = dns.changes().create(managedZone=self.zone_name,
                                     project=PROJECT,
                                     body={
                                         'kind': 'dns#change',
                                         'additions': additions,
                                         'deletions': deletions
                                     })
      response = request.execute()
      logger.info(response)
      return response
    except Exception as e:  # pylint: disable=broad-except
      logger.exception(e)


class Instance:
  """
  Get details of a GCE instance using resource name
  """

  def __init__(self, resource_name):
    instance_details = re.search(
        r'^projects\/(.*)\/zones\/(.*)\/instances\/(.*)$', resource_name)
    self.project = instance_details.group(1)
    self.zone = instance_details.group(2)
    self.instance_name = instance_details.group(3)

  def get_instance_metadata(self):
    try:
      request = compute.instances().get(project=self.project,
                                        zone=self.zone,
                                        instance=self.instance_name)
      response = request.execute()
      logger.info(response)
      return response
    except Exception as e:  # pylint: disable=broad-except
      logger.exception(e)

  def internal_ip(self):
    instance_metadata = self.get_instance_metadata()
    return instance_metadata['networkInterfaces'][0]['networkIP']
