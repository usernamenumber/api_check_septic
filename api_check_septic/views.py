from django.http import JsonResponse
from django.shortcuts import render
from .utils import has_septic 

# api_version is currently ignored
def check_septic(request, api_version=None):
    """
    API endpoint returning a JSON dict representing the result of  a call to `utils.has_septic()` 

    URL parameters `address` and `zipcode` are required or the view will report failure.

    If successful, the result of `has_septic()` is stored as a boolean under the `result` key
    
    If an error is caught, it is recorded under the `error` key

    :param request: django request object
    :param api_version: provided by the parent API, but currently ignored
    :returns: JSON like `{"address": STRING, "zipcode": STRING, "result": BOOL|None, "error": STRING|None}`
    :rtype dict:
    """
    address = request.GET.get('address')
    zipcode = request.GET.get('zipcode')

    if not (address and zipcode):
        return JsonResponse({
            "error": f"Missing one or more required url parameters: address ({address}), zipcode ({zipcode})",
        })

    data = {
        "address": address,
        "zipcode": zipcode,
        "result": None,
        "error": None,
    }
    try:
        data["result"] = has_septic(address, zipcode)
    except Exception as e:
        data["error"] = str(e)

    return JsonResponse(data)
