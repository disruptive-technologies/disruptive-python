from __future__ import annotations

# Standard library imports.
import time
import json
from typing import Optional

# Third-party imports.
import requests

# Project imports
import disruptive as dt
import disruptive.log as dtlog
import disruptive.errors as dterrors
from disruptive.dtresponses import DTResponse


def generic_request(method: str, url: str, **kwargs):
    """
    Generic request function used by most resource methods.

    Parameters
    ----------
    method : str
        Request method to use.
    url : str
        Target endpoint of request.
    params : dict, optional
        Parameters dictionary to include in request.
    headers : dict, optional
        Headers dictionary to include in request.
    body : dict, optional
        Body dictionary to include in request.
    data : str, optional
        Encoded data string to include in request.
    request_timeout : int, optional
        Number of seconds before request times out.
        Overwrites dt.request_timeout settings if provided.
    request_retries : int, optional
        Number of times to retry a request.
        Overwrites dt.request_retries settings if provided.
    auth : Auth, optional
        Object for authenticating the REST API.
        Overwrites dt.auth if provided.
    skip_auth : bool
        If provided with a value of True, excludes authentication header.

    Returns
    -------
    response : DTResponse
        An object representing the response and its content.

    """

    # Unpack all kwargs at once here for readability.
    params = kwargs['params'] if 'params' in kwargs else {}
    headers = kwargs['headers'] if 'headers' in kwargs else {}
    body = kwargs['body'] if 'body' in kwargs else None
    data = kwargs['data'] if 'data' in kwargs else None
    if 'request_timeout' in kwargs:
        request_timeout = kwargs['request_timeout']
    else:
        request_timeout = dt.request_timeout
    if 'request_retries' in kwargs:
        request_retries = kwargs['request_retries']
    else:
        request_retries = dt.request_retries

    # If this is the first recursive depth, retry counter is set to 1.
    # Adding it to kwargs like this is maybe a little weird, but is done as
    # the function is called recursively, which may results
    # in "double argument" problems if taken in as an argument.
    # Also, it works just fine.
    if 'retry_count' not in kwargs:
        kwargs['retry_count'] = 1

    # Add authorization header to request except when explicitly told not to.
    if 'skip_auth' not in kwargs or kwargs['skip_auth'] is False:
        # If provided, override package-wide auth with argument.
        if 'auth' in kwargs:
            headers['Authorization'] = kwargs['auth'].get_token()
        else:
            headers['Authorization'] = dt.auth.get_token()

    # Send request.
    dtlog.log('Request [{}] to {}.'.format(method, url))
    response = __send_request(
        method=method,
        url=url,
        params=params,
        headers=headers,
        body=body,
        data=data,
        timeout=request_timeout,
    )

    # Parse errors.
    # If there is any hope at all that a retry might resolve the error,
    # should_retry will be True. (eg. a 401).
    error, should_retry, retry_after = dterrors.parse_error(
        # status_code=response.status_code,
        status_code=response.status_code,
        headers=response.headers,
        retry_count=kwargs['retry_count'],
    )

    # Check if retry is required.
    if should_retry and kwargs['retry_count'] < request_retries:

        dtlog.log("Got error {}. Will retry up to {} more times".format(
            error,
            dt.request_retries - kwargs['retry_count']
        ))

        # Sleep if necessary.
        if retry_after is not None:
            time.sleep(retry_after)

        # Retry.
        kwargs['retry_count'] += 1
        generic_request(
            method=method,
            url=url,
            **kwargs,
        )

    # Raise error if present.
    if error is not None:
        raise error(response.data)

    return response.data


def auto_paginated_list(url: str,
                        pagination_key: str,
                        params: dict[str, str] = {},
                        **kwargs,
                        ):
    # Initialize output list.
    results = []

    # Unpack all kwargs at once here for readability.
    params = kwargs['params'] if 'params' in kwargs else {}
    if 'page_size' in kwargs:
        params['pageSize'] = kwargs['page_size']

    # Loop until paging has finished.
    while True:
        response = generic_request("GET", url, params=params, **kwargs)
        results += response[pagination_key]

        if len(response['nextPageToken']) > 0:
            params['pageToken'] = response['nextPageToken']
        else:
            break

    return results


def stream(url: str, **kwargs):
    # Set ping parameters.
    ping_interval = 10
    ping_jitter = 2

    # Unpack kwargs.
    params = kwargs['params'] if 'params' in kwargs else {}
    headers = kwargs['headers'] if 'headers' in kwargs else {}
    if 'request_retries' in kwargs:
        request_retries = kwargs['request_retries']
    else:
        request_retries = dt.request_retries

    # If provided, override package-wide auth with argument.
    if 'auth' in kwargs:
        headers['Authorization'] = kwargs['auth'].get_token()
    else:
        headers['Authorization'] = dt.auth.get_token()

    # Set up a simple catch-all retry policy.
    nth_retry = 0
    while nth_retry <= request_retries:
        try:
            # Set up a stream connection.
            # Connection will timeout and reconnect if no single event
            # is received in an interval of ping_interval + ping_jitter.
            dtlog.log('Starting stream...')
            stream = requests.get(
                url=url,
                stream=True,
                timeout=ping_interval + ping_jitter,
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
            if nth_retry < request_retries:
                dtlog.log('Connection lost. Retry {}/{}.'.format(
                    nth_retry+1,
                    request_retries,
                ))

                # Exponential backoff in sleep time.
                time.sleep(2**nth_retry)
                nth_retry += 1
            else:
                break


def __send_request(method: str,
                   url: str,
                   params: dict,
                   headers: dict,
                   body: Optional[dict],
                   data: Optional[str],
                   timeout: int,
                   ):
    response = requests.request(
        method=method,
        url=url,
        params=params,
        headers=headers,
        json=body,
        data=data,
        timeout=timeout)

    return DTResponse(
        response.json(),
        response.status_code,
        dict(response.headers),
    )
