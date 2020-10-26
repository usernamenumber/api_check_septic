# `has_septic` API endpoint

## Premise

This is a simple django API endpoint, which may or may not have been created as part of a job interview. The endpoint provides a generic way to check whether a given property, identified by an address and zip code, has a septic tank. It uses [the housecanary API](https://api-docs.housecanary.com) but is designed to make this easy to modify in a way that is transparent to users.

## Assumptions

The following are assumptions I made for this project. Under normal circumstances I would have validated each of these with a co-worker before writing anything, and will revise the project if any of my assumptions prove incorrect, but for the sake of moving things along quickly, I took my best guesses for now.

1. The endpoint should provide the caller with a boolean value indicating presence of a septic tank at a given property
1. Only properties with the `sewer` detail "septic" (case insensitive) according to [hosuecanary's property/details API](https://api-docs.housecanary.com/#property-details) are assumed to have septic tanks
1. A property is identified by a street address and zip code
    - The housecanary docs say their API will also support city+state instead of zipcode, but say zipcode is the standard so I chose not to support city+state to keep things simple.
1. The address and zipcode should be provided to the endpoint via URL parameters, i.e. `?address=...&zipcode=...` (the same way HouseCanary works)
    - This is the simplest approach for a standalone API, but if the endpoint is intended for integration with an existing API then address and zip, or an ID from which those values can be derived, could be provided earlier in the path, for example if the parent project has a url pattern like

        ```py
        path('api/v<api_version>/home/<home_id>/has_septic',
            include('api_check_septic.urls')
        )
        ```

        and provides a way to get an address and zipcode from `home_id`.

## Next Steps

These are things I would do given more time

- Authentication: a few aspects of it...
  - Depending on the use case, it could make sense to get the housecanary credentials from a parameter store instead of environment variables.
  - Our API requires no authentication of its own. How/whether this is implemented depends on the design of the larger API into which this endpoint would be integrated.
- Caching: depending on how frequently the endpoint is called for the same address in a short amount of time, it could help scalability to cache results
  - One way to do this would be with a simple in-memory kvs if we're ok trading volatility for speed.
  - Since the values returned by housecanary are unlikely to change, if we really wanted to minimize external calls we could cache all query results in the local database forever (or until manually removed), so we only go out to housecanary once for each queried property combination.
- API versioning: the project as written incorporates a version number into the URL as a best practice, but it is currently ignored.
- Better testing: there are a few things we could test but don't, for example...
  - We mock out `requests.get()` but don't have a test that will fail if `check_septic` is ever updated to use a different http mechanism
  - We don't have a test that confirms housecanary credentials are loaded from environment variables and passed to `requests.get()`

## Setup and Execution

1. Clone this repo
2. Run tests

    ```sh
    python ./manage.py test
    ```

3. Set up housecanary authentication

    ```sh
    export API_CHECK_SEPTIC__HOUSECANARY_USER="my_housecanary_api_key"
    export API_CHECK_SEPTIC__HOUSECANARY_PASSWORD="my_housecanary_api_secret"
    ```

4. Start django

    ```sh
    python ./manage.py runserver
    ```

5. Try it out

    ```sh
    ADDRESS="14 Evergreen Terrace"
    ZIPCODE="12345"
    curl -s "http://localhost:8000/api/v1/property/has_septic?address=$(echo $ADDRESS | tr ' ' +)&zipcode=${ZIPCODE}"
    ```

## Example

Output example, using [jq](https://stedolan.github.io/jq/) for nicely formatted results:

```sh
$ ADDRESS="14 Evergreen Terrace"
$ ZIPCODE="12345"
$ curl -s "http://localhost:8000/api/v1/property/has_septic?address=$(echo $ADDRESS | tr ' ' +)&zipcode=${ZIPCODE}" | jq '.'
{
  "address": "14 Evergreen Terrace",
  "zipcode": "02144",
  "result": true,
  "error": null
}
```
