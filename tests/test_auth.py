# Third-party imports.
import pytest

# Project imports.
import disruptive as dt
from disruptive.authentication import OAuth

# Test imports.
import tests.mock_responses as mock_responses


class TestOAuth():

    def test_constructors(self, request_mock):
        # Update the response json with a mock token response.
        res = mock_responses.auth_tokens['fresh']
        request_mock.json = res

        # Call the two classmethod constructors.
        dt.OAuth.authenticate('', '', '')
        auth_instance = dt.OAuth.create('', '', '')

        # Assert token post request sent for each.
        request_mock.assert_request_count(2)

        # Assert instance of OAuth class.
        assert isinstance(dt.auth, OAuth)
        assert isinstance(auth_instance, OAuth)

    def test_token_refresh(self, request_mock):
        # Update the response json with an expired token response.
        res = mock_responses.auth_tokens['expired']
        request_mock.json = res

        # Create an authentication object.
        auth = dt.OAuth.create('', '', '')

        # Verify expired token.
        assert auth.has_expired()

        # Update the response json with a fresh token response.
        res = mock_responses.auth_tokens['fresh']
        request_mock.json = res

        # Call the get_token method to force a refresh.
        auth.get_token()

        # Verify non-expired token.
        assert not auth.has_expired()

    def test_raise_missing_credential(self):
        # Verify TypeError raised at missing input credential.
        with pytest.raises(TypeError):
            dt.OAuth.authenticate(None, '', '')
        with pytest.raises(TypeError):
            dt.OAuth.authenticate('', None, '')
        with pytest.raises(TypeError):
            dt.OAuth.authenticate('', '', None)
