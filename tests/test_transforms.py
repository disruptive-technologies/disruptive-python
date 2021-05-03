# Standard library imports
from datetime import datetime, timezone, timedelta

# Third-party imports.
import pytest

# Project imports.
import disruptive.transforms as dttrans
import disruptive.errors as dterrors


class TestTransforms():

    def test_base64_encode(self):
        outp = 'ZXhhbXBsZV9zdHJpbmc='
        assert dttrans.base64_encode('example_string') == outp

    def test_to_iso8601_invalid_type(self):
        inp = {'timestamp': '1970-01-01T00:00:00Z'}
        with pytest.raises(dterrors.TypeError):
            dttrans.to_iso8601(inp)

    def test_to_iso8601_none(self):
        inp = None
        outp = None
        assert dttrans.to_iso8601(inp) == outp

    def test_to_iso8601_string_utc(self):
        inp = '1970-01-01T00:00:00Z'
        outp = '1970-01-01T00:00:00Z'
        assert dttrans.to_iso8601(inp) == outp

    def test_to_iso8601_string_tz_offset(self):
        inp = '1970-01-01T00:00:00+02:00'
        outp = '1970-01-01T00:00:00+02:00'
        assert dttrans.to_iso8601(inp) == outp

    def test_to_iso8601_string_invalid_tz(self):
        inp = '1970-01-01T00:00:00+02:00Z'
        with pytest.raises(dterrors.FormatError):
            dttrans.to_iso8601(inp)

    def test_to_iso8601_datetime_with_tz_utc(self):
        inp = datetime(1970, 1, 1, tzinfo=timezone(timedelta(hours=0)))
        outp = '1970-01-01T00:00:00+00:00'
        assert dttrans.to_iso8601(inp) == outp

    def test_to_iso8601_datetime_with_tz_offset(self):
        inp = datetime(1970, 1, 1, tzinfo=timezone(timedelta(hours=2)))
        outp = '1970-01-01T00:00:00+02:00'
        assert dttrans.to_iso8601(inp) == outp

    def test_to_iso8601_datetime_without_tz(self):
        inp = datetime(1970, 1, 1)
        outp = '1970-01-01T00:00:00Z'
        assert dttrans.to_iso8601(inp) == outp

    def test_to_datetime_invalid_type(self):
        inp = {'timestamp': datetime(1970, 1, 1)}
        with pytest.raises(dterrors.TypeError):
            dttrans.to_datetime(inp)

    def test_to_datetime_none(self):
        inp = None
        outp = None
        assert dttrans.to_datetime(inp) == outp

    def test_to_datetime_missing_tz(self):
        inp = '1970-01-01T00:00:00'
        with pytest.raises(dterrors.FormatError):
            dttrans.to_datetime(inp)

    def test_to_datetime_tz_utc(self):
        inp = '1970-01-01T00:00:00Z'
        outp = datetime(1970, 1, 1, tzinfo=timezone(timedelta(hours=0)))
        assert dttrans.to_datetime(inp) == outp

    def test_to_datetime_tz_offset(self):
        inp = '1970-01-01T00:00:00+02:00'
        outp = datetime(1970, 1, 1, tzinfo=timezone(timedelta(hours=2)))
        assert dttrans.to_datetime(inp) == outp

    def test_to_datetime_already_datetime(self):
        inp = datetime(1970, 1, 1, tzinfo=timezone(timedelta(hours=2)))
        outp = datetime(1970, 1, 1, tzinfo=timezone(timedelta(hours=2)))
        assert dttrans.to_datetime(inp) == outp

    def test_validate_iso8601_format_valid(self):
        inp1 = '1970-01-01T00:00:00Z'
        assert dttrans.validate_iso8601_format(inp1) is True

        inp2 = '1970-01-01T00:00:00+00:00'
        assert dttrans.validate_iso8601_format(inp2) is True

    def test_validate_iso8601_format_missing_tz(self):
        inp = '1970-01-01T00:00:00'
        assert dttrans.validate_iso8601_format(inp) is False

    def test_validate_iso8601_format_date_only(self):
        inp = '1970-01-01'
        assert dttrans.validate_iso8601_format(inp) is False
