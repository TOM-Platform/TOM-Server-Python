import pytest

from APIs.maps.location_data import LocationData
from APIs.maps.maps import get_locations
from APIs.osm_api import osm_api
from APIs.osm_api.osm_api import find_locations_osm
from base_keys import PLACES_OPTION_OSM

locations_sample_response_osm = [LocationData(address='Marina Bay Sands, 10, Bayfront Avenue, Bayfront, '
                                                      'Downtown Core, Singapore, Central, 018956, Singapore',
                                              name='Marina Bay Sands',
                                              latitude=1.2836965,
                                              longitude=103.8607226),
                                 LocationData(address='Marina Bay Sands, 10, Bayfront Avenue, Bayfront, '
                                                      'Downtown Core, Singapore, Central, 018957, Singapore',
                                              name='Marina Bay Sands',
                                              latitude=1.2817723,
                                              longitude=103.8574685),
                                 LocationData(address='Marina Bay Sands, Bayfront Avenue, Bayfront, Downtown '
                                                      'Core, Singapore, Central, 018971, Singapore',
                                              name='Marina Bay Sands',
                                              latitude=1.2856255,
                                              longitude=103.8610678)]


@pytest.mark.asyncio
async def test_locations_osm_success(monkeypatch):
    async def mock_find_locations_osm_impl(search_text):
        return locations_sample_response_osm

    monkeypatch.setattr(osm_api, 'find_locations_osm', mock_find_locations_osm_impl)
    response = await get_locations("Marina Bay Sands", PLACES_OPTION_OSM)
    assert response == locations_sample_response_osm
