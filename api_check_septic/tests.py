import requests
from copy import deepcopy
from django.test import Client, TestCase
from django.urls import reverse
from unittest.mock import Mock, patch
from .utils import has_septic

HC_PROPERTY_DETAILS_DEFAULT = {
    "property/details": {
        "api_code_description": "ok",
        "api_code": 0,
        "result": {
            "property": {
                "air_conditioning": "yes",
                "attic": False,
                "basement": "full_basement",
                "building_area_sq_ft": 1824,
                "building_condition_score": 5,
                "building_quality_score": 3,
                "construction_type": "Wood",
                "exterior_walls": "wood_siding",
                "fireplace": False,
                "full_bath_count": 2,
                "garage_parking_of_cars": 1,
                "garage_type_parking": "underground_basement",
                "heating": "forced_air_unit",
                "heating_fuel_type": "gas",
                "no_of_buildings": 1,
                "no_of_stories": 2,
                "number_of_bedrooms": 4,
                "number_of_units": 1,
                "partial_bath_count": 1,
                "pool": True,
                "property_type": "Single Family Residential",
                "roof_cover": "Asphalt",
                "roof_type": "Wood truss",
                "site_area_acres": 0.119,
                "style": "colonial",
                "total_bath_count": 2.5,
                "total_number_of_rooms": 7,
                "sewer": "municipal",
                "subdivision" : "CITY LAND ASSOCIATION",
                "water": "municipal",
                "year_built": 1957,
                "zoning": "RH1"
            },

            "assessment":{
                "apn": "0000 -1111",
                "assessment_year": 2015,
                "tax_year": 2015,
                "total_assessed_value": 1300000.0,
                "tax_amount": 15199.86
            }
        }
    }
}

# This is arguably over-engineered, but as you'll see below it
# makes the creation of tests for multiple sewer types trivial
class CheckSepticTestMixIn(object):
    """
    Mixin for basic tests against calls to the `check_septic` API endpoint

    To implement a test with this mixin, define a class that inherits
    from it and TestCase (in that order) and define at least 
    `sewer_type` and `expected_result` as class properties.
    See https://api-docs.housecanary.com/#property-details for
    expected sewer types.

    The test performs a GET request against the check_septic API endpoint 
    URL, with self.address and self.zipcode as url parameters. During the 
    test, external calls to Housing Canary are mocked to return data for a 
    home with self.sewer_type.

    The test validates that the call returns self.expected_result.
    """
    address = '123 Foo st'
    zipcode = '02144'

    @property
    def sewer_type(self):
        raise NotImplementedError("sewer_type must be defined by the test class")

    @property
    def expected_result(self):
        raise NotImplementedError("expected_result must be defined by the test class")

    def _mock_external_response(self):
        """
        Simulate housing canary results for a home with the given sewer type

        Returns a mocked version of the requests module such that .get()ing any URL 
        returns property details json for a house with the given sewer type
        """
        requestsMock = Mock()
        responseMock = Mock()

        json_response = deepcopy(HC_PROPERTY_DETAILS_DEFAULT)
        json_response["property/details"]["result"]["property"]["sewer"] = self.sewer_type
        responseMock.json.return_value = json_response
        requestsMock.get.return_value = responseMock

        return requestsMock

    def setUp(self):
        url = reverse('check_septic', kwargs={'api_version':1})
        url += f"?address={self.address}&zipcode={self.zipcode}"

        with patch('api_check_septic.utils.requests', self._mock_external_response()):
            self.response = Client().get(url).json()

    def shortDescription(self):
        return f"check_septic API call returns {self.expected_response} and no error message when sewer type is {self.sewer_type}"

    def test_result(self):
        self.assertTrue('result' in self.response)
        self.assertEqual(self.response['result'], self.expected_result)
        self.assertIsNone(self.response.get('error', None))

class TestApiCall_SepticSewer_NoAddress(CheckSepticTestMixIn, TestCase):
    sewer_type = 'septic'
    address = ''
    expected_result = False

    def shortDescription(self):
        return f"check_septic API call returns an error message when no address is given"

    def test_result(self):
        self.assertTrue('error' in self.response)
        self.assertIsNotNone(self.response['error'])

class TestApiCall_SepticSewer(CheckSepticTestMixIn, TestCase):
    sewer_type = 'septic'
    expected_result = True

class TestApiCall_MunicipalSewer(CheckSepticTestMixIn, TestCase):
    sewer_type = 'municipal'
    expected_result = False

# The rest are probably overkill, but the mixin makes it so
# simple we may as well be thorough
class TestApiCall_NoSewer(CheckSepticTestMixIn, TestCase):
    sewer_type = 'none'
    expected_result = False

class TestApiCall_StormSewer(CheckSepticTestMixIn, TestCase):
    sewer_type = 'storm'
    expected_result = False

class TestApiCall_YesSewer(CheckSepticTestMixIn, TestCase):
    sewer_type = 'yes'
    expected_result = False