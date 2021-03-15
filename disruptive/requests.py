# Standard library imports.
import time
import json

# Third-party imports.
import requests

# Project imports
import disruptive as dt
import disruptive.log as dtlog
import disruptive.errors as dterrors
import disruptive.responses as dtresponses


def get(url: str,
        params={},
        headers={},
        timeout=None,
        auth=None
        ):
    return __construct_request(
        "GET",
        url,
        params,
        headers,
        timeout=timeout,
        auth=auth
    )


def post(url: str,
         body: dict = None,
         data: str = None,
         headers: dict = {},
         authorize: bool = True,
         auth=None,
         ):
    return __construct_request(
        "POST",
        url,
        body=body,
        data=data,
        headers=headers,
        authorize=authorize,
        auth=auth,
    )


def patch(url: str, body: dict, auth=None):
    return __construct_request("PATCH", url, body=body, auth=auth)


def delete(url: str, auth=None):
    return __construct_request("DELETE", url, auth=auth)


def auto_paginated_list(
        url: str,
        pagination_key: str,
        params: dict = {},
        page_size: int = None,
        auth=None,
):
    results = []
    if page_size is not None:
        params['pageSize'] = page_size

    while True:
        response = __construct_request("GET", url, params=params, auth=auth)
        results += response[pagination_key]

        if len(response['nextPageToken']) > 0:
            params['pageToken'] = response['nextPageToken']
        else:
            break

    return results


def generator_list(
        url: str,
        pagination_key: str,
        params: dict = {},
        page_size: int = 100,
        auth=None,
):
    params['pageSize'] = page_size

    while True:
        response = __construct_request("GET", url, params, auth=auth)

        yield response[pagination_key]

        if len(response['nextPageToken']) > 0:
            params['pageToken'] = response['nextPageToken']
        else:
            break


def __construct_request(
        method: str,
        url: str,
        params: dict = {},
        headers: dict = {},
        body: dict = None,
        data: str = None,
        retry_count: int = 1,
        timeout: int = None,
        authorize: bool = True,
        auth=None,
):
    # Add headers to request
    if authorize:
        if auth is None:
            headers["Authorization"] = dt.auth.get_token()
        else:
            headers["Authorization"] = auth.get_token()
    for key in headers.keys():
        headers[key] = headers[key]

    # Set default timeout if explicitly provided.
    if timeout is None:
        timeout = dt.request_timeout

    # Send request.
    dtlog.log('Request [{}] to {}.'.format(method, url))
    response = __send_request(
        method=method,
        url=url,
        params=params,
        headers=headers,
        body=body,
        data=data,
        timeout=timeout,
    )

    # Parse errors.
    # If there is any hope at all that a retry might resolve the error,
    # should_retry will be True. (eg. a 401).
    error, should_retry, retry_after = dterrors.parse_error(
        # status_code=response.status_code,
        status_code=response.status_code,
        headers=response.headers,
        retry_count=retry_count,
    )

    # Check if retry is required
    if should_retry and retry_count < dt.max_request_retries:

        dtlog.log("Got error {}. Will retry up to {} more times".format(
            error,
            dt.max_request_retries - retry_count
        ))

        # Sleep if necessary.
        if retry_after is not None:
            time.sleep(retry_after)

        # Retry.
        __construct_request(
            method=method,
            url=url,
            params=params,
            headers=headers,
            body=body,
            data=data,
            retry_count=retry_count + 1,
            authorize=authorize,
        )

    # Raise error if present.
    if error is not None:
        raise error(response.data)

    return response.data


def __send_request(method,
                   url,
                   params,
                   headers,
                   body,
                   data,
                   timeout,
                   ):
    response = requests.request(
        method=method,
        url=url,
        params=params,
        headers=headers,
        json=body,
        data=data,
        timeout=timeout)

    return dtresponses.DTResponse(
        response.json(),
        response.status_code,
        response.headers
    )


def stream(url: str, params: dict):
    # Construct uURL.
    url = dt.base_url + url

    # Set streaming parameters and headers.
    params['ping_interval'] = '{}s'.format(dt.ping_interval)
    headers = {
        'Authorization': dt.auth.get_token()
    }

    # Set up a simple catch-all retry policy.
    nth_retry = 0
    while nth_retry <= dt.max_request_retries:
        try:
            # Set up a stream connection.
            # Connection will timeout and reconnect if no single event
            # is received in an interval of ping_interval + ping_jitter.
            dtlog.log('Starting stream...')
            stream = requests.get(
                url=url,
                stream=True,
                timeout=dt.ping_interval + dt.ping_jitter,
                params=params,
                headers=headers,
            )

            # Iterate through the events as they come in (one per line).
            for line in stream.iter_lines():
                # Decode the response payload and break on error.
                payload = json.loads(line.decode('ascii'))
                if 'result' not in payload:
                    break

                # Reset retry counter.
                nth_retry = 0

                # Check for ping event.
                event = payload['result']['event']
                if event['eventType'] == 'ping':
                    dtlog.log('Got ping')
                    continue

                yield event

        except KeyboardInterrupt:
            break

        except Exception as e:
            print(e)
            # Print the error and try again up to max_request_retries.
            if nth_retry < dt.max_request_retries:
                dtlog.log('Connection lost. Retry {}/{}.'.format(
                    nth_retry+1,
                    dt.max_request_retries,
                ))

                # Exponential backoff in sleep time.
                time.sleep(2**nth_retry)
                nth_retry += 1
            else:
                break
