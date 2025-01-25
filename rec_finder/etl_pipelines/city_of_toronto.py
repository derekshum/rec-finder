# Toronto Open Data is stored in a CKAN instance. It's APIs are documented
# here:
# https://docs.ckan.org/en/latest/api/
from datetime import datetime, timedelta

import requests
from io import StringIO
import csv

from rec_finder.etl_pipelines.exceptions import UnexpectedDataFormatException
from rec_finder.models import Event, Venue

BASE_URL = 'https://ckan0.cf.opendata.inter.prod-toronto.ca'


def get_resource(package: dict, resource_name: str) -> (csv.DictReader |
                                                        None):
    for idx, resource in enumerate(package['result']['resources']):
        if resource['datastore_active'] and resource['name'] == resource_name:
            url = BASE_URL + '/datastore/dump/' + resource['id']
            resource_dump_data = requests.get(url).text
            reader = csv.DictReader(StringIO(resource_dump_data))
            return reader


def refresh_venues(package: dict) -> dict[int, int]:
    '''
    Updates the venue information in the database and returns a dictionary
    to convert from this data pull's Location ID to the database's venue_id.
    Throws an UnexpectedDataFormatException if the data is not in the expected
    format.
    '''
    venue_reader = get_resource(package, 'Locations')
    if not venue_reader:
        raise UnexpectedDataFormatException(
            'Expected venue resource was not found. Update aborted.'
        )

    # define expected information headers
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
            raise UnexpectedDataFormatException(
                f'Expected venue header {header} was not found. Update aborted.'
            )

    # dict to convert from City of Toronto Location ID to db Venue id
    venue_dict: dict[int, Venue] = {}

    street_address_headers = [street_no, street_no_suffix, street_name,
                              street_type, street_direction]
    for row in venue_reader:
        venue_name: str = row[location_name]
        venue_address: str = ','.join(filter(
            None, [' '.join(filter(
                None, [row[header] for header in street_address_headers]
            )), row[postal_code]]
        ))

        matching_venues = Venue.objects.filter(
            name=venue_name,
            address=venue_address
        )
        if len(matching_venues) > 0:
            venue_dict[row[location_id]] = matching_venues[0]
            print(f'Found {len(matching_venues)} match(es) for {venue_name}.')
            continue
        venue = Venue(name=venue_name, address=venue_address)
        venue.save()
        venue_dict[row[location_id]] = venue
        print(f'Adding new venue {venue_name}.')
    return venue_dict


def refresh_events(package: dict, venues_dict: dict) -> None:
    '''
    Updates the event information in the database. Throws an
    UnexpectedDataFormatException if the data is not in the expected format.
    '''
    event_reader = get_resource(package, 'Drop-in')
    if not event_reader:
        raise UnexpectedDataFormatException(
            'Expected event resource was not found. Event update aborted.'
        )

    # define expected information headers
    location_id = 'Location ID'
    course_title = 'Course Title'
    start_date_time = 'Start Date Time'
    start_hour = 'Start Hour'
    start_min = 'Start Minute'
    end_hour = 'End Hour'
    end_min = 'End Min'  # yep, it's 'Start Minute' and 'End Min'

    for header in [location_id, course_title, start_date_time, start_hour,
                   start_min, end_hour, end_min]:
        if header not in event_reader.fieldnames:
            raise UnexpectedDataFormatException(
                f'Expected event header {header} not found. Event update '
                f'aborted.'
            )

    for row in event_reader:
        event_name = row[course_title]
        event_start_time = datetime.fromisoformat(row[start_date_time]) \
                           + timedelta(
                                hours=int(row[start_hour]),
                                minutes=int(row[start_min]) \
                                    if row[start_min] else 0
                            )
        event_end_time = datetime.fromisoformat(row[start_date_time]) \
                           + timedelta(
                                hours=int(row[end_hour]),
                                minutes=int(row[end_min]) \
                                    if row[end_min] else 0
                            )
        venue = venues_dict[row[location_id]]

        matching_events = Event.objects.filter(
            venue=venue,
            name=event_name,
            start_time=event_start_time,
            end_time=event_end_time,
        )
        if len(matching_events) > 0:
            print(f'Found {len(matching_events)} match(es) for {event_name}.')
            continue
        Event(
            venue=venue,
            name=event_name,
            start_time=event_start_time,
            end_time=event_end_time,
        ).save()
        print(f'Adding new event {event_name}.')


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

    venues_dict = refresh_venues(package)

    refresh_events(package, venues_dict)
