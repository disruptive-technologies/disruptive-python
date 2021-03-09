# Standard library imports.
from unittest.mock import patch

# Third-party imports.
import pytest

# Project imports.
import disruptive as dt
import disruptive.errors as errors
from tests.framework import MockRequest, TestEndpoint


class TestResponseStatusCodes(TestEndpoint):
    # @classmethod
    # def setup_class(cls):
    #     cls.mock_request_patcher = patch('requests.request')
    #     cls.mock_request = cls.mock_request_patcher.start()

    # @classmethod
    # def teardown_class(cls):
    #     cls.mock_request_patcher.stop()

    def test_error_code_400(self):
        # Set response status code to represent test.
        self.mock_request.return_value = MockRequest(status_code=400)

        # Try to authenticate. This sends a POST request internally.
        with pytest.raises(errors.BadRequest):
            dt.OAuth.authenticate('', '', '')

    def test_error_code_401(self):
        # Set response status code to represent test.
        self.mock_request.return_value = MockRequest(status_code=401)

        # Call the service, which will send a request to the server.
        with pytest.raises(errors.Unauthenticated):
            dt.OAuth.authenticate('', '', '')

    def test_error_code_403(self):
        # Set response status code to represent test.
        self.mock_request.return_value = MockRequest(status_code=403)

        # Call the service, which will send a request to the server.
        with pytest.raises(errors.Forbidden):
            dt.OAuth.authenticate('', '', '')

    def test_error_code_404(self):
        # Set response status code to represent test.
        self.mock_request.return_value = MockRequest(status_code=404)

        # Call the service, which will send a request to the server.
        with pytest.raises(errors.NotFound):
            dt.OAuth.authenticate('', '', '')

    def test_error_code_409(self):
        # Set response status code to represent test.
        self.mock_request.return_value = MockRequest(status_code=409)

        # Call the service, which will send a request to the server.
        with pytest.raises(errors.Conflict):
            dt.OAuth.authenticate('', '', '')

    def test_error_code_429(self):
        # Set response status code to represent test.
        self.mock_request.return_value = MockRequest(status_code=429)

        # Call the service, which will send a request to the server.
        with pytest.raises(errors.TooManyRequests):
            dt.OAuth.authenticate('', '', '')

    def test_error_code_500(self):
        # Set response status code to represent test.
        self.mock_request.return_value = MockRequest(status_code=500)

        # Call the service, which will send a request to the server.
        with pytest.raises(errors.InternalServerError):
            dt.OAuth.authenticate('', '', '')

    def test_error_code_503(self):
        # Set response status code to represent test.
        self.mock_request.return_value = MockRequest(status_code=503)

        # Call the service, which will send a request to the server.
        with pytest.raises(errors.InternalServerError):
            dt.OAuth.authenticate('', '', '')

    def test_error_code_504(self):
        # Set response status code to represent test.
        self.mock_request.return_value = MockRequest(status_code=504)

        # Call the service, which will send a request to the server.
        with pytest.raises(errors.InternalServerError):
            dt.OAuth.authenticate('', '', '')
