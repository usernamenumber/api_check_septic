import os
import requests
import urllib

def _housecanary_property_details(address, zipcode):
    """
    Query the housecanary property_details API for a given property

    A valid housecanary key and secret must be stored in the 
    `API_CHECK_SEPTIC__HOUSECANARY_USER` and 
    `API_CHECK_SEPTIC__HOUSECANARY_PASSWORD` environment variables,
    respectively for the query to work.

    :param address: the property's street address
    :param zipcode: the property's zip code
    :returns: JSON dict as described at https://api-docs.housecanary.com/#property-details
    :rtype dict:
    """
    hc_user = os.getenv('API_CHECK_SEPTIC__HOUSECANARY_USER', 'SET ME')
    hc_password = os.getenv('API_CHECK_SEPTIC__HOUSECANARY_PASSWORD', 'SET ME')
    address = urllib.parse.quote_plus(address)
    url = f'https://api.housecanary.com/v2/property/details?address={address}&zipcode={zipcode}'
    # no error checking because we want failures here to be handled by the caller
    return requests.get(url, auth=(hc_user, hc_password)).json()

def has_septic(address, zipcode):
    """
    Return a boolean indicating whether the property at the given address has a septic tank

    :param address: the property's street address
    :param zipcode: the property's zip code
    :returns: True if septic tank is present, otherwise False
    :rtype bool:
    """
    data = _housecanary_property_details(address, zipcode) 
    if 'property/details' not in data:
        raise RuntimeError(f"Server returned no data and the message: '{data.get('message', '')}'")
    elif not data['property/details'].get('result', None):
        # https://api-docs.housecanary.com/#response-codes-and-errors
        api_code = data['property/details'].get('api_code', "unknown")
        api_code_desc = data['property/details'].get('api_code_description', "unknown")
        raise RuntimeError(f"Server returned no data and API code {api_code} ('{api_code_desc}')")
    sewer_type = data["property/details"]["result"]["property"]["sewer"] 
    return sewer_type.lower() == 'septic'