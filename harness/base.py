import logging

import requests  # ty: ignore[unresolved-import]

from harness.assertion import Assertion
from harness.constants import environment_data
from harness.utils import new_idempotency_key

logger = logging.getLogger(__name__)


# fresh key if none given
def idempotency_header(key=None):
    if key is None:
        key = new_idempotency_key()
    return {"Idempotency-Key": key}


class ApiResponse:
    def __init__(self, http_response):
        self.assertion = Assertion()
        self.status_code = http_response.status_code
        content_type = http_response.headers.get("content-type", "")
        is_json = "application/json" in content_type
        # 204 replies have a json content-type but no body
        if is_json and http_response.content:
            self.body = http_response.json()
        else:
            self.body = http_response.text

    # failure message has the body, returns self so calls chain
    def expect(self, status_code):
        self.assertion.assert_status(self.status_code, status_code, f"body {self.body}")
        return self

    # checks the documented error envelope, returns the error object
    def expect_error(self, status_code, error_code, what_proven):
        self.expect(status_code)
        self.assertion.assert_equal(
            actual_result=self.body["error"]["code"],
            expected_result=error_code,
            what_proven=what_proven,
            label="error code",
            detail=self.body,
        )
        return self.body["error"]


# get and post shared by both clients, a client method is just endpoint + payload
class HttpClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def get(self, endpoint):
        return self._send("GET", endpoint)

    def post(self, endpoint, json=None, headers=None):
        return self._send("POST", endpoint, json, headers)

    def _send(self, method, endpoint, json=None, headers=None):
        url = self.base_url + endpoint
        message = f"sending {method} {url}"
        if json is not None:
            message = message + f", body {json}"
        if headers is not None:
            message = message + f", headers {headers}"
        logger.info(message)

        http_response = self.session.request(
            method,
            url,
            json=json,
            headers=headers,
            timeout=environment_data["timeout"],
        )
        response = ApiResponse(http_response)

        if response.body:
            logger.info(f"got {response.status_code} back with {response.body}")
        else:
            logger.info(f"got {response.status_code} back with no body")
        return response
