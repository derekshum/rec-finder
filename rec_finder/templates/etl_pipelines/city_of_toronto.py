# Toronto Open Data is stored in a CKAN instance. It's APIs are documented
# here:
# https://docs.ckan.org/en/latest/api/

import requests
from io import StringIO
import csv

from rec_finder.models import Event, Venue

BASE_URL = 'https://ckan0.cf.opendata.inter.prod-toronto.ca'


def get_resource(package: list | dict, resource_name: str) -> (csv.DictReader |
                                                               None):
    for idx, resource in enumerate(package['result']['resources']):
        if resource['datastore_active'] and resource['name'] == resource_name:
            url = BASE_URL + '/datastore/dump/' + resource['id']
            resource_dump_data = requests.get(url).text
            reader = csv.DictReader(StringIO(resource_dump_data))
            return reader


def refresh_data() -> str:
    '''
    This function pulls in the City of Toronto's recreation locations and drop
    in events, adding any new to the app's database. Returns a status message.
    '''

    # To retrieve the metadata for this package and its resources, use the
    # package name in this page's URL:
    url = BASE_URL + '/api/3/action/package_show'
    params = {'id': 'registered-programs-and-drop-in-courses-offering'}
    package = requests.get(url, params=params).json()

    venue_reader = get_resource(package, 'Locations')
    if not venue_reader:
        return 'Expected venue resource was not found. Update aborted.'

    location_id = 'Location ID'
    location_name = 'Location Name'
    street_no = 'Street No'
    street_no_suffix = 'Street No Suffix'
    street_name = 'Street Name'
    street_type = 'Street Type'
    street_direction = 'Street Direction'
    postal_code = 'Postal Code'

    # check that all headers are present
    for header in [location_id, location_name, street_no, street_no_suffix,
                   street_name, street_type, street_direction, postal_code]:
        if header not in venue_reader.fieldnames:
            return 'Expected venue headings were not found. Update aborted.'

    street_address_headers = [street_no, street_no_suffix, street_name,
                              street_type, street_direction]
    for row in venue_reader:
        venue = Venue(
            name=row[location_name],
            address=','.join(filter(
                None, [' '.join(filter(
                    None, [row[header] for header in street_address_headers]
                )), row[postal_code]]
            )))
        venue.save()
        break   # TODO remove

    # TODO event_headers, event_data = get_resource(package, 'Drop-in')
