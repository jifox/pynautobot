"""API tests."""

import unittest
from unittest.mock import patch

import pynautobot

HOST = "http://localhost:8000"

def_kwargs = {
    "token": "abc123",
}

# Keys are app names, values are arbitrarily selected endpoints
# We use dcim and ipam since they have unique app classes
# and circuits because it does not. We don't add other apps/endpoints
# beyond 'circuits' as they all use the same code as each other
endpoints = {
    "dcim": "devices",
    "ipam": "prefixes",
    "circuits": "circuits",
}


class ApiTestCase(unittest.TestCase):
    """API test."""

    @patch(
        "requests.sessions.Session.post",
    )
    @patch("pynautobot.api.version", "2.0")
    def test_get(self, *_):
        api = pynautobot.api(HOST, **def_kwargs)
        self.assertTrue(api)

    @patch(
        "requests.sessions.Session.post",
    )
    @patch("pynautobot.api.version", "2.0")
    def test_sanitize_url(self, *_):
        api = pynautobot.api("http://localhost:8000/", **def_kwargs)
        self.assertTrue(api)
        self.assertEqual(api.base_url, "http://localhost:8000/api")

    @patch("pynautobot.api.version", "2.0")
    def test_verify_true(self, *_):
        api = pynautobot.api("http://localhost:8000/", **def_kwargs)
        self.assertTrue(api)
        self.assertTrue(api.http_session.verify)

    @patch("pynautobot.api.version", "2.0")
    def test_verify_false(self, *_):
        api = pynautobot.api("http://localhost:8000/", verify=False, **def_kwargs)
        self.assertTrue(api)
        self.assertFalse(api.http_session.verify)

    @patch("pynautobot.api.version", "2.0")
    def test_useragent_set(self, *_):
        api = pynautobot.api("http://localhost:8000/", **def_kwargs)
        self.assertEqual(api.http_session.headers["user-agent"], f"python-pynautobot/{pynautobot.__version__}")


class ApiVersionTestCase(unittest.TestCase):
    """API version test."""

    class ResponseHeadersWithVersion:  # pylint: disable=too-few-public-methods
        """Response headers with version."""

        headers = {"API-Version": "1.999"}
        ok = True

    @patch(
        "requests.sessions.Session.get",
        return_value=ResponseHeadersWithVersion(),
    )
    def test_api_version(self, *_):
        with self.assertRaises(ValueError) as error:
            pynautobot.api(HOST)
        self.assertEqual(
            str(error.exception), "Nautobot version 1 detected, please downgrade pynautobot to version 1.x"
        )

    class ResponseHeadersWithoutVersion:  # pylint: disable=too-few-public-methods
        """Response headers without version."""

        headers = {}
        ok = True

    @patch(
        "requests.sessions.Session.get",
        return_value=ResponseHeadersWithoutVersion(),
    )
    def test_api_version_not_found(self, *_):
        api = pynautobot.api(
            HOST,
        )
        self.assertEqual(api.version, "")

    class ResponseHeadersWithVersion2:  # pylint: disable=too-few-public-methods
        """Response headers with version 2."""

        headers = {"API-Version": "2.0"}
        ok = True

    @patch(
        "requests.sessions.Session.get",
        return_value=ResponseHeadersWithVersion2(),
    )
    def test_api_version_2(self, *_):
        api = pynautobot.api(
            HOST,
        )
        self.assertEqual(api.version, "2.0")


class ApiStatusTestCase(unittest.TestCase):
    """API status test."""

    class ResponseWithStatus:  # pylint: disable=too-few-public-methods
        """Response with status."""

        ok = True

        def json(self):
            """Return JSON."""
            return {
                "nautobot-version": "1.3.2",
            }

    @patch(
        "requests.sessions.Session.get",
        return_value=ResponseWithStatus(),
    )
    @patch("pynautobot.api.version", "2.0")
    def test_api_status(self, *_):
        api = pynautobot.api(
            HOST,
        )
        self.assertEqual(api.status()["nautobot-version"], "1.3.2")


class ApiRetryTestCase(unittest.TestCase):
    """API retry test."""

    def test_api_retry(self):
        with patch("pynautobot.api.version", "2.0"):
            api = pynautobot.api(
                "http://any.url/",
                retries=2,
            )
            # Assert that the retries are set on the session
            self.assertEqual(api.http_session.adapters["http://"].max_retries.total, 2)
            self.assertEqual(api.http_session.adapters["https://"].max_retries.total, 2)
