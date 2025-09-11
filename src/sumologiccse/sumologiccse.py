import http.cookiejar as cookielib
import json
import logging
import os
import re
from typing import Any, Optional

import requests


class SumoLogicCSEError(Exception):
    """Base exception for SumoLogic CSE API errors."""
    pass


class AuthenticationError(SumoLogicCSEError):
    """Raised when authentication fails."""
    pass


class APIError(SumoLogicCSEError):
    """Raised when the API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class ConfigurationError(SumoLogicCSEError):
    """Raised when there's a configuration error."""
    pass


class DataError(SumoLogicCSEError):
    """Raised when there's an issue with data parsing or validation."""
    pass


# Set up logging
LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
    level=LOGLEVEL,
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class SumoLogicCSE:
    """
    A class to interact with the Sumo Logic Cloud SIEM API.
    """

    def __init__(
        self,
        accessId=os.environ.get("SUMO_ACCESS_ID"),
        accessKey=os.environ.get("SUMO_ACCESS_KEY"),
        endpoint="https://api.sumologic.com/api/sec",
        caBundle=None,
        cookieFile="cookies.txt",
    ):
        """
        Initialize the SumoLogicCSE object.

        :param accessId: Sumo Logic access ID. Defaults to SUMO_ACCESS_ID env var.
        :param accessKey: Sumo Logic access key. Defaults to SUMO_ACCESS_KEY env var.
        :param endpoint: API endpoint. Defaults to 'https://api.sumologic.com/api/sec'.
        :param caBundle: CA bundle for SSL verification
        :param cookieFile: File to store cookies
        :raises AuthenticationError: If credentials are missing
        :raises ConfigurationError: If configuration is invalid
        """
        # Validate credentials
        if not accessId or not accessKey:
            raise AuthenticationError(
                "Missing credentials. Provide accessId and accessKey parameters or set "
                "SUMO_ACCESS_ID and SUMO_ACCESS_KEY environment variables."
            )

        # Validate and set endpoint
        self.endpoint = self._validate_endpoint(endpoint)

        # Initialize session with proper error handling
        try:
            self.session = requests.Session()
            self.session.auth = (accessId, accessKey)
            self.DEFAULT_VERSION = "v1"
            self.session.headers = {
                "content-type": "application/json",
                "accept": "application/json",
            }

            if caBundle is not None:
                self.session.verify = caBundle
                logger.debug("Using custom CA bundle for SSL verification")

            # Initialize cookies with error handling
            try:
                cj = cookielib.FileCookieJar(cookieFile)
                self.session.cookies = cj
                logger.debug(f"Cookie jar initialized: {cookieFile}")
            except OSError as e:
                logger.warning(f"Could not initialize cookie jar {cookieFile}: {e}")
                # Continue without cookies rather than failing

            # Log successful initialization (without credentials)
            logger.info("SumoLogic CSE client initialized successfully")

        except Exception as e:
            raise ConfigurationError(f"Failed to initialize client: {e}") from e

    def _validate_endpoint(self, endpoint: str) -> str:
        """
        Validate and normalize the endpoint URL.

        :param endpoint: The endpoint to validate
        :return: Normalized endpoint URL
        :raises ConfigurationError: If endpoint is invalid
        """
        if endpoint is None:
            endpoint = "https://api.sumologic.com/api/sec"
        elif re.match(r"^(au|fra|mum|us2|mon|dub|tky)$", endpoint):
            endpoint = f"https://api.{endpoint}.sumologic.com/api/sec"
        elif re.match(r"^(prod|us1)$", endpoint):
            endpoint = "https://api.sumologic.com/api/sec"
        # If it's already a full URL, use as-is

        if endpoint.endswith("/"):
            raise ConfigurationError("Endpoint should not end with a slash character")

        # Basic URL validation
        if not (endpoint.startswith("https://") or endpoint.startswith("http://")):
            raise ConfigurationError("Endpoint must be a valid HTTP/HTTPS URL")

        logger.debug(f"Using endpoint: {endpoint}")
        return endpoint

    def get_versioned_endpoint(self, version):
        """
        Get the versioned endpoint URL.

        :param version: API version
        :return: Versioned endpoint URL
        """
        return self.endpoint + f"/{version}"

    def _handle_response(self, response: requests.Response, method: str) -> requests.Response:
        """
        Handle HTTP response with proper error handling and logging.

        :param response: The HTTP response object
        :param method: The API method that was called
        :return: The response object if successful
        :raises APIError: If the response indicates an error
        :raises AuthenticationError: If authentication failed
        """
        try:
            # Log the request details
            logger.debug(f"{response.request.method} {response.url} -> {response.status_code}")

            if response.status_code == 401:
                logger.error("Authentication failed - check credentials")
                raise AuthenticationError("Authentication failed. Check your access ID and key.")
            elif response.status_code == 403:
                logger.error("Access denied - insufficient permissions")
                raise APIError("Access denied. Check your permissions.", response.status_code, response.text)
            elif 400 <= response.status_code < 600:
                error_msg = f"API request failed: {method}"
                try:
                    # Try to extract error details from JSON response
                    error_data = response.json()
                    if "message" in error_data:
                        error_msg = f"API error: {error_data['message']}"
                    elif "error" in error_data:
                        error_msg = f"API error: {error_data['error']}"
                except (ValueError, json.JSONDecodeError):
                    # Fall back to response text if JSON parsing fails
                    error_msg = f"API error: {response.text[:200]}" if response.text else error_msg

                logger.error(f"HTTP {response.status_code}: {error_msg}")
                raise APIError(error_msg, response.status_code, response.text)

            return response

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during {method}: {e}")
            raise APIError(f"Network error: {e}") from e

    def delete(self, method, params=None, version=None):
        """
        Send a DELETE request.

        :param method: API method
        :param params: Request parameters
        :param version: API version
        :return: Response object
        :raises APIError: If the request fails
        """
        version = version or self.DEFAULT_VERSION
        endpoint = self.get_versioned_endpoint(version)

        try:
            logger.debug(f"DELETE {endpoint + method}")
            r = self.session.delete(endpoint + method, params=params)
            return self._handle_response(r, f"DELETE {method}")
        except requests.exceptions.RequestException as e:
            logger.error(f"DELETE request failed for {method}: {e}")
            raise APIError(f"DELETE request failed: {e}") from e

    def get(self, method, params=None, version=None):
        """
        Send a GET request.

        :param method: API method
        :param params: Request parameters
        :param version: API version
        :return: Response object
        :raises APIError: If the request fails
        """
        version = version or self.DEFAULT_VERSION
        endpoint = self.get_versioned_endpoint(version)

        try:
            logger.debug(f"GET {endpoint + method}")
            r = self.session.get(endpoint + method, params=params)
            return self._handle_response(r, f"GET {method}")
        except requests.exceptions.RequestException as e:
            logger.error(f"GET request failed for {method}: {e}")
            raise APIError(f"GET request failed: {e}") from e

    def post(self, method, params, headers=None, version=None):
        """
        Send a POST request.

        :param method: API method
        :param params: Request parameters
        :param headers: Request headers
        :param version: API version
        :return: Response object
        :raises APIError: If the request fails
        """
        version = version or self.DEFAULT_VERSION
        endpoint = self.get_versioned_endpoint(version)

        try:
            logger.debug(f"POST {endpoint + method}")
            r = self.session.post(
                endpoint + method, data=json.dumps(params), headers=headers
            )
            return self._handle_response(r, f"POST {method}")
        except (json.JSONEncodeError, TypeError) as e:
            logger.error(f"JSON encoding failed for POST {method}: {e}")
            raise DataError(f"Invalid JSON data: {e}") from e
        except requests.exceptions.RequestException as e:
            logger.error(f"POST request failed for {method}: {e}")
            raise APIError(f"POST request failed: {e}") from e

    def _safe_json_parse(self, response: requests.Response, context: str = "") -> dict[str, Any]:
        """
        Safely parse JSON response with proper error handling.

        :param response: The HTTP response object
        :param context: Context for error messages (e.g., method name)
        :return: Parsed JSON data
        :raises DataError: If JSON parsing fails
        """
        try:
            if not response.text:
                logger.warning(f"Empty response received for {context}")
                return {}

            data = response.json()
            logger.debug(f"Successfully parsed JSON response for {context}")
            return data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response for {context}: {e}")
            logger.debug(f"Response text: {response.text[:500]}")
            raise DataError(f"Invalid JSON response from API: {e}") from e

    def post_file(self, method, params, headers=None, version=None):
        """
        Handle file uploads via a separate POST request.

        :param method: API method
        :param params: Request parameters
        :param headers: Request headers
        :param version: API version
        :return: Response object
        :raises APIError: If the request fails
        :raises DataError: If file operations fail
        """
        version = version or self.DEFAULT_VERSION
        endpoint = self.get_versioned_endpoint(version)

        try:
            # Validate required parameters
            if "full_file_path" not in params or "file_name" not in params:
                raise DataError("Missing required parameters: full_file_path and file_name")

            post_params = {"merge": params.get("merge", False)}

            # Read file with proper error handling
            try:
                with open(params["full_file_path"], "rb") as f:
                    file_data = f.read()
                logger.debug(f"Read {len(file_data)} bytes from {params['full_file_path']}")
            except OSError as e:
                logger.error(f"Failed to read file {params['full_file_path']}: {e}")
                raise DataError(f"Cannot read file: {e}") from e

            files = {"file": (params["file_name"], file_data)}

            logger.debug(f"POST FILE {endpoint + method}")
            r = requests.post(
                endpoint + method,
                files=files,
                params=post_params,
                auth=self.session.auth,
                headers=headers,
            )
            return self._handle_response(r, f"POST FILE {method}")

        except requests.exceptions.RequestException as e:
            logger.error(f"File upload failed for {method}: {e}")
            raise APIError(f"File upload failed: {e}") from e

    def put(self, method, params, headers=None, version=None):
        """
        Send a PUT request.

        :param method: API method
        :param params: Request parameters
        :param headers: Request headers
        :param version: API version
        :return: Response object
        :raises APIError: If the request fails
        """
        version = version or self.DEFAULT_VERSION
        endpoint = self.get_versioned_endpoint(version)

        try:
            logger.debug(f"PUT {endpoint + method}")
            r = self.session.put(
                endpoint + method, data=json.dumps(params), headers=headers
            )
            return self._handle_response(r, f"PUT {method}")
        except (json.JSONEncodeError, TypeError) as e:
            logger.error(f"JSON encoding failed for PUT {method}: {e}")
            raise DataError(f"Invalid JSON data: {e}") from e
        except requests.exceptions.RequestException as e:
            logger.error(f"PUT request failed for {method}: {e}")
            raise APIError(f"PUT request failed: {e}") from e

    def get_insights_all(self, q=None, nextPageToken=None):
        """
        Retrieve all insights.

        :param q: Query parameter
        :param nextPageToken: Token for the next page
        :return: JSON response
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"q": q, "nextPageToken": nextPageToken}
        logger.info(f"Fetching insights with query: {q}")
        response = self.get("/insights/all", params)
        return self._safe_json_parse(response, "get_insights_all")

    def get_insights(self, q=None, max_pages=5):
        """
        Retrieve insights with pagination.

        :param q: Query parameter
        :param max_pages: Maximum number of pages to retrieve
        :return: List of insights
        """
        insights = []
        pages = 0
        next_page_token = None
        while pages < max_pages:
            pages += 1
            i = self.get_insights_all(q, next_page_token)
            if len(i["data"]["objects"]) > 0:
                insights = insights + i["data"]["objects"]
            else:
                logger.debug("no results")

            next_page_token = i["data"]["nextPageToken"]

            if next_page_token is None:
                logger.debug(
                    str(len(insights)) + " insights at last page: " + str(pages)
                )
                break
        return insights

    def get_insights_list(self, q=None, offset=0, limit=20):
        """
        Retrieve a list of insights with offset and limit.

        :param q: Query parameter
        :param offset: Offset for pagination
        :param limit: Limit for pagination
        :return: JSON response
        """
        params = {"q": q, "offset": offset, "limit": limit}
        response = self.get("/insights", params)
        return json.loads(response.text)

    def query_insights(self, q=None, offset=0, limit=20):
        """
        Query insights with pagination.

        :param q: Query parameter
        :param offset: Offset for pagination
        :param limit: Limit for pagination
        :return: List of insights
        """
        insights = []
        pages = 0
        batchsize = 20 if limit > 20 else limit

        remaining = limit
        while remaining > 0:
            i = self.get_insights_list(q, offset=pages, limit=batchsize)
            logger.debug(
                "batch:"
                + str(pages)
                + " remaining: "
                + str(remaining)
                + " batchsize:"
                + str(batchsize)
            )
            logger.debug("returned: " + str(len(i["data"]["objects"])))
            if len(i["data"]["objects"]) > 0:
                insights = insights + i["data"]["objects"]
                remaining = remaining - len(i["data"]["objects"])
            else:
                logger.debug("no results")
                remaining = 0

            if not i["data"]["hasNextPage"]:
                logger.debug(
                    str(len(insights))
                    + " insights at last page: "
                    + str(len(i["data"]["objects"]))
                )
                break
            pages += batchsize
            batchsize = 20 if remaining > 20 else remaining
        return insights

    def get_insight(self, insight_id):
        """
        Retrieve a specific insight by ID.

        :param insight_id: Insight ID
        :return: JSON response
        """
        response = self.get(f"/insights/{insight_id}")
        return json.loads(response.text)

    def get_insight_statuses(self):
        """
        Retrieve all insight statuses.

        :return: JSON response
        """
        response = self.get("/insight-status")
        return json.loads(response.text)

    def update_insight_resolution_status(self, insight_id, resolution, status):
        """
        Update the resolution status of an insight.

        :param insight_id: Insight ID
        :param resolution: Resolution status
        :param status: Status
        :return: JSON response
        """
        body = {"resolution": resolution, "status": status}
        response = self.put(f"/insights/{insight_id}/status", body)
        return json.loads(response.text)

    def add_insight_comment(self, insight_id, comment):
        """
        Add a comment to an insight.

        :param insight_id: Insight ID
        :param comment: Comment text
        :return: JSON response
        """
        body = {"body": comment}
        response = self.post(f"/insights/{insight_id}/comments", body)
        return json.loads(response.text)

    def get_rules(self, q=None, offset=0, limit=20):
        """
        Retrieve rules with optional query and pagination.

        :param q: Query parameter for filtering rules
        :param offset: Offset for pagination
        :param limit: Limit for pagination (max 100)
        :return: JSON response
        """
        params = {"q": q, "offset": offset, "limit": limit}
        response = self.get("/rules", params)
        return json.loads(response.text)

    def get_rule(self, rule_id):
        """
        Retrieve a specific rule by ID.

        :param rule_id: Rule ID
        :return: JSON response
        """
        response = self.get(f"/rules/{rule_id}")
        return json.loads(response.text)

    def query_rules(self, q=None, offset=0, limit=20):
        """
        Query rules with pagination handling.

        :param q: Query parameter for filtering rules
        :param offset: Offset for pagination
        :param limit: Limit for pagination
        :return: List of rules
        """
        rules = []
        pages = 0
        batchsize = min(limit, 20) if limit > 20 else limit

        remaining = limit
        while remaining > 0:
            r = self.get_rules(q, offset=pages, limit=batchsize)
            logger.debug(f"batch:{pages} remaining:{remaining} batchsize:{batchsize}")
            logger.debug(f"returned: {len(r['data']['objects'])}")

            if len(r["data"]["objects"]) > 0:
                rules.extend(r["data"]["objects"])
                remaining -= len(r["data"]["objects"])
            else:
                logger.debug("no results")
                remaining = 0

            if not r["data"]["hasNextPage"]:
                logger.debug(f"{len(rules)} rules at last page")
                break

            pages += batchsize
            batchsize = min(20, remaining)

        return rules
