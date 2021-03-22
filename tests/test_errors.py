# Third-part imports.
import pytest

# Project imports.
import disruptive as dt
import disruptive.errors as errors


class TestResponseStatusCodes():

    def test_error_code_400(self, request_mock):
        # Set response status code to represent test.
        request_mock.status_code = 400

        # Try to authenticate. This sends a POST request internally.
        with pytest.raises(errors.BadRequest):
            dt.Device.get_device('', '')

    def test_error_code_401(self, request_mock):
        # Set response status code to represent test.
        request_mock.status_code = 401

        # Call the service, which will send a request to the server.
        with pytest.raises(errors.Unauthenticated):
            dt.Device.get_device('', '')

    def test_error_code_403(self, request_mock):
        # Set response status code to represent test.
        request_mock.status_code = 403

        # Call the service, which will send a request to the server.
        with pytest.raises(errors.Forbidden):
            dt.Device.get_device('', '')

    def test_error_code_404(self, request_mock):
        # Set response status code to represent test.
        request_mock.status_code = 404

        # Call the service, which will send a request to the server.
        with pytest.raises(errors.NotFound):
            dt.Device.get_device('', '')

    def test_error_code_409(self, request_mock):
        # Set response status code to represent test.
        request_mock.status_code = 409

        # Call the service, which will send a request to the server.
        with pytest.raises(errors.Conflict):
            dt.Device.get_device('', '')

    def test_error_code_429(self, request_mock):
        # Set response status code to represent test.
        request_mock.status_code = 429

        # Call the service, which will send a request to the server.
        with pytest.raises(errors.TooManyRequests):
            dt.Device.get_device('', '')

    def test_error_code_500(self, request_mock):
        # Set response status code to represent test.
        request_mock.status_code = 500

        # Call the service, which will send a request to the server.
        with pytest.raises(errors.InternalServerError):
            dt.Device.get_device('', '')

        # Assert expected retry attempts.
        request_mock.assert_request_count(3)

    def test_error_code_503(self, request_mock):
        # Set response status code to represent test.
        request_mock.status_code = 503

        # Call the service, which will send a request to the server.
        with pytest.raises(errors.InternalServerError):
            dt.Device.get_device('', '')

        # Assert expected retry attempts.
        request_mock.assert_request_count(3)

    def test_error_code_504(self, request_mock):
        # Set response status code to represent test.
        request_mock.status_code = 504

        # Call the service, which will send a request to the server.
        with pytest.raises(errors.InternalServerError):
            dt.Device.get_device('', '')

        # Assert expected retry attempts.
        request_mock.assert_request_count(3)
