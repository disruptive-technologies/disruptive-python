
# Authentication scheme.
from disruptive.authentication import Auth

# When auth is an instance of Auth set with the default constructor,
# the project is globally unauthorized, throwing an Unauthorized error at call.
# To authorize globally, overwrite with one of the following classmethods.
#
# auth = disruptive.Auth.basic(key_id, secret)
# auth = disruptive.Auth.oauth(key_id, secret, email)
auth = Auth()

# Resources.
from disruptive.resources.device import Device
from disruptive.resources.dataconnector import Dataconnector
from disruptive.resources.organization import Organization
from disruptive.resources.project import Project
from disruptive.resources.stream import Stream
from disruptive.resources.event_history import EventHistory

# If True, debug information is sent to stdout.
log = False

# REST API base URL of which all endpoints are an expansion.
base_url = 'https://api.disruptive-technologies.com/v2'

# When streaming it is good practice to ping the connection periodically.
# The ping interval is set in the initial request that establishes a TCP
# connection. By including a timeout with some jitter, the connection will
# automatically reconnect if a ping is not heard within the expected range.
ping_interval = 10
ping_jitter = 2
request_timeout = 3
max_request_retries = 3
