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
        response_text: Optional[str] = None,
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

    def _handle_response(
        self, response: requests.Response, method: str
    ) -> requests.Response:
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
            logger.debug(
                f"{response.request.method} {response.url} -> {response.status_code}"
            )

            if response.status_code == 401:
                logger.error("Authentication failed - check credentials")
                raise AuthenticationError(
                    "Authentication failed. Check your access ID and key."
                )
            elif response.status_code == 403:
                logger.error("Access denied - insufficient permissions")
                raise APIError(
                    "Access denied. Check your permissions.",
                    response.status_code,
                    response.text,
                )
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
                    error_msg = (
                        f"API error: {response.text[:200]}"
                        if response.text
                        else error_msg
                    )

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
        except (TypeError, ValueError) as e:
            logger.error(f"JSON encoding failed for POST {method}: {e}")
            raise DataError(f"Invalid JSON data: {e}") from e
        except requests.exceptions.RequestException as e:
            logger.error(f"POST request failed for {method}: {e}")
            raise APIError(f"POST request failed: {e}") from e

    def _safe_json_parse(
        self, response: requests.Response, context: str = ""
    ) -> dict[str, Any]:
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
                raise DataError(
                    "Missing required parameters: full_file_path and file_name"
                )

            post_params = {"merge": params.get("merge", False)}

            # Read file with proper error handling
            try:
                with open(params["full_file_path"], "rb") as f:
                    file_data = f.read()
                logger.debug(
                    f"Read {len(file_data)} bytes from {params['full_file_path']}"
                )
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
        except (TypeError, ValueError) as e:
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

    # =================================================================
    # Configuration Endpoints
    # =================================================================

    def get_insights_configuration(self):
        """
        Get global insights configuration.

        :return: JSON response with insights configuration
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info("Fetching global insights configuration")
        response = self.get("/insights-configuration")
        return self._safe_json_parse(response, "get_insights_configuration")

    def get_context_actions(self, limit: int = 100, token: str = None):
        """
        Get all context actions.

        :param limit: Maximum number of results to return
        :param token: Continuation token for pagination
        :return: JSON response with context actions
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"limit": limit}
        if token:
            params["token"] = token

        logger.info("Fetching context actions")
        response = self.get("/context-actions", params)
        return self._safe_json_parse(response, "get_context_actions")

    def get_context_action(self, action_id: str):
        """
        Get a specific context action by ID.

        :param action_id: The context action ID
        :return: JSON response with context action details
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info(f"Fetching context action: {action_id}")
        response = self.get(f"/context-actions/{action_id}")
        return self._safe_json_parse(response, "get_context_action")

    def get_insight_statuses(self):
        """
        Get all defined or custom insight statuses.

        :return: JSON response with insight statuses
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info("Fetching insight statuses")
        response = self.get("/insight-status")
        return self._safe_json_parse(response, "get_insight_statuses")

    def get_insight_status(self, status_id: str):
        """
        Get a specific insight status by ID.

        :param status_id: The insight status ID
        :return: JSON response with insight status details
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info(f"Fetching insight status: {status_id}")
        response = self.get(f"/insight-status/{status_id}")
        return self._safe_json_parse(response, "get_insight_status")

    def get_insight_resolutions(self):
        """
        Get all defined or custom insight resolutions.

        :return: JSON response with insight resolutions
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info("Fetching insight resolutions")
        response = self.get("/insight-resolutions")
        return self._safe_json_parse(response, "get_insight_resolutions")

    def get_insight_resolution(self, resolution_id: str):
        """
        Get a specific insight resolution by ID.

        :param resolution_id: The insight resolution ID
        :return: JSON response with insight resolution details
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info(f"Fetching insight resolution: {resolution_id}")
        response = self.get(f"/insight-resolutions/{resolution_id}")
        return self._safe_json_parse(response, "get_insight_resolution")

    # =================================================================
    # Custom Entity and Insight Endpoints
    # =================================================================

    def get_custom_entity_types(self, limit: int = 100, token: str = None):
        """
        Get all custom entity types.

        :param limit: Maximum number of results to return
        :param token: Continuation token for pagination
        :return: JSON response with custom entity types
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"limit": limit}
        if token:
            params["token"] = token

        logger.info("Fetching custom entity types")
        response = self.get("/custom-entity-types", params)
        return self._safe_json_parse(response, "get_custom_entity_types")

    def get_custom_entity_type(self, entity_type_id: str):
        """
        Get a specific custom entity type by ID.

        :param entity_type_id: The custom entity type ID
        :return: JSON response with custom entity type details
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info(f"Fetching custom entity type: {entity_type_id}")
        response = self.get(f"/custom-entity-types/{entity_type_id}")
        return self._safe_json_parse(response, "get_custom_entity_type")

    def get_custom_insights(self, limit: int = 100, token: str = None):
        """
        Get all custom insights.

        :param limit: Maximum number of results to return
        :param token: Continuation token for pagination
        :return: JSON response with custom insights
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"limit": limit}
        if token:
            params["token"] = token

        logger.info("Fetching custom insights")
        response = self.get("/custom-insights", params)
        return self._safe_json_parse(response, "get_custom_insights")

    def get_custom_insight(self, insight_id: str):
        """
        Get a specific custom insight by ID.

        :param insight_id: The custom insight ID
        :return: JSON response with custom insight details
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info(f"Fetching custom insight: {insight_id}")
        response = self.get(f"/custom-insights/{insight_id}")
        return self._safe_json_parse(response, "get_custom_insight")

    # =================================================================
    # Match Lists and Columns Endpoints
    # =================================================================

    def get_match_lists(self, limit: int = 100, token: str = None):
        """
        Get all match lists.

        :param limit: Maximum number of results to return
        :param token: Continuation token for pagination
        :return: JSON response with match lists
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"limit": limit}
        if token:
            params["token"] = token

        logger.info("Fetching match lists")
        response = self.get("/match-lists", params)
        return self._safe_json_parse(response, "get_match_lists")

    def get_match_list(self, list_id: str):
        """
        Get a specific match list by ID.

        :param list_id: The match list ID
        :return: JSON response with match list details
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info(f"Fetching match list: {list_id}")
        response = self.get(f"/match-lists/{list_id}")
        return self._safe_json_parse(response, "get_match_list")

    def get_match_list_items(self, list_id: str, limit: int = 100, token: str = None):
        """
        Get items from a specific match list.

        :param list_id: The match list ID
        :param limit: Maximum number of results to return
        :param token: Continuation token for pagination
        :return: JSON response with match list items
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"limit": limit}
        if token:
            params["token"] = token

        logger.info(f"Fetching match list items for list: {list_id}")
        response = self.get(f"/match-lists/{list_id}/items", params)
        return self._safe_json_parse(response, "get_match_list_items")

    def get_match_list_item(self, list_id: str, item_id: str):
        """
        Get a specific item from a match list.

        :param list_id: The match list ID
        :param item_id: The match list item ID
        :return: JSON response with match list item details
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info(f"Fetching match list item: {item_id} from list: {list_id}")
        response = self.get(f"/match-lists/{list_id}/items/{item_id}")
        return self._safe_json_parse(response, "get_match_list_item")

    def get_custom_match_list_columns(self, limit: int = 100, token: str = None):
        """
        Get all custom match list columns.

        :param limit: Maximum number of results to return
        :param token: Continuation token for pagination
        :return: JSON response with custom match list columns
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"limit": limit}
        if token:
            params["token"] = token

        logger.info("Fetching custom match list columns")
        response = self.get("/custom-match-list-columns", params)
        return self._safe_json_parse(response, "get_custom_match_list_columns")

    def get_custom_match_list_column(self, column_id: str):
        """
        Get a specific custom match list column by ID.

        :param column_id: The custom match list column ID
        :return: JSON response with custom match list column details
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info(f"Fetching custom match list column: {column_id}")
        response = self.get(f"/custom-match-list-columns/{column_id}")
        return self._safe_json_parse(response, "get_custom_match_list_column")

    # =================================================================
    # Entity Management Endpoints
    # =================================================================

    def get_entities(self, q: str = None, limit: int = 100, offset: int = 0):
        """
        Get entities with optional query filtering.

        :param q: Query parameter for filtering entities
        :param limit: Maximum number of results to return
        :param offset: Offset for pagination
        :return: JSON response with entities
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"limit": limit, "offset": offset}
        if q:
            params["q"] = q

        logger.info(f"Fetching entities with query: {q}")
        response = self.get("/entities", params)
        return self._safe_json_parse(response, "get_entities")

    def get_entity(self, entity_id: str):
        """
        Get a specific entity by ID.

        :param entity_id: The entity ID
        :return: JSON response with entity details
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info(f"Fetching entity: {entity_id}")
        response = self.get(f"/entities/{entity_id}")
        return self._safe_json_parse(response, "get_entity")

    def get_related_entities_by_id(self, entity_id: str):
        """
        Get entities related to a specific entity ID.

        :param entity_id: The entity ID
        :return: JSON response with related entities
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info(f"Fetching related entities for: {entity_id}")
        response = self.get(f"/entities/{entity_id}/related")
        return self._safe_json_parse(response, "get_related_entities_by_id")

    def get_entity_groups(self, limit: int = 100, token: str = None):
        """
        Get all entity group configurations.

        :param limit: Maximum number of results to return
        :param token: Continuation token for pagination
        :return: JSON response with entity groups
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"limit": limit}
        if token:
            params["token"] = token

        logger.info("Fetching entity groups")
        response = self.get("/entity-groups", params)
        return self._safe_json_parse(response, "get_entity_groups")

    def get_entity_group(self, group_id: str):
        """
        Get a specific entity group by ID.

        :param group_id: The entity group ID
        :return: JSON response with entity group details
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info(f"Fetching entity group: {group_id}")
        response = self.get(f"/entity-groups/{group_id}")
        return self._safe_json_parse(response, "get_entity_group")

    def get_entity_criticality_configs(self, limit: int = 100, token: str = None):
        """
        Get all custom entity criticality configurations.

        :param limit: Maximum number of results to return
        :param token: Continuation token for pagination
        :return: JSON response with entity criticality configs
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"limit": limit}
        if token:
            params["token"] = token

        logger.info("Fetching entity criticality configurations")
        response = self.get("/entity-criticality-configs", params)
        return self._safe_json_parse(response, "get_entity_criticality_configs")

    def get_entity_criticality_config(self, config_id: str):
        """
        Get a specific entity criticality configuration by ID.

        :param config_id: The entity criticality configuration ID
        :return: JSON response with entity criticality config details
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info(f"Fetching entity criticality config: {config_id}")
        response = self.get(f"/entity-criticality-configs/{config_id}")
        return self._safe_json_parse(response, "get_entity_criticality_config")

    # =================================================================
    # Lookup Tables Endpoints
    # =================================================================

    def get_customer_sourced_lookup_tables(self, limit: int = 100, token: str = None):
        """
        Get all customer-created lookup tables.

        :param limit: Maximum number of results to return
        :param token: Continuation token for pagination
        :return: JSON response with customer lookup tables
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"limit": limit}
        if token:
            params["token"] = token

        logger.info("Fetching customer sourced lookup tables")
        response = self.get("/customer-sourced-lookup-tables", params)
        return self._safe_json_parse(response, "get_customer_sourced_lookup_tables")

    def get_customer_sourced_lookup_table(self, table_id: str):
        """
        Get a specific customer-created lookup table by ID.

        :param table_id: The lookup table ID
        :return: JSON response with lookup table details
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info(f"Fetching customer sourced lookup table: {table_id}")
        response = self.get(f"/customer-sourced-lookup-tables/{table_id}")
        return self._safe_json_parse(response, "get_customer_sourced_lookup_table")

    # =================================================================
    # Log Mappings and Reporting Endpoints
    # =================================================================

    def get_log_mappings(self, limit: int = 100, token: str = None):
        """
        Get all defined log mappings.

        :param limit: Maximum number of results to return
        :param token: Continuation token for pagination
        :return: JSON response with log mappings
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"limit": limit}
        if token:
            params["token"] = token

        logger.info("Fetching log mappings")
        response = self.get("/log-mappings", params)
        return self._safe_json_parse(response, "get_log_mappings")

    def get_log_mapping(self, mapping_id: str):
        """
        Get a specific log mapping by ID.

        :param mapping_id: The log mapping ID
        :return: JSON response with log mapping details
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info(f"Fetching log mapping: {mapping_id}")
        response = self.get(f"/log-mappings/{mapping_id}")
        return self._safe_json_parse(response, "get_log_mapping")

    def get_log_mapping_vendors_and_products(self):
        """
        Get all available log mapping vendors and products.

        :return: JSON response with vendors and products
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info("Fetching log mapping vendors and products")
        response = self.get("/log-mappings/vendors-and-products")
        return self._safe_json_parse(response, "get_log_mapping_vendors_and_products")

    def get_insight_counts(self, start_time: str, end_time: str, timezone: str = "UTC"):
        """
        Get insight counts for reporting volumes.

        :param start_time: Start time in ISO format
        :param end_time: End time in ISO format
        :param timezone: Timezone (default: UTC)
        :return: JSON response with insight counts
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"startTime": start_time, "endTime": end_time, "timezone": timezone}

        logger.info(f"Fetching insight counts from {start_time} to {end_time}")
        response = self.get("/insight-counts", params)
        return self._safe_json_parse(response, "get_insight_counts")

    def get_signal_counts(self, start_time: str, end_time: str, timezone: str = "UTC"):
        """
        Get signal counts for reporting volumes.

        :param start_time: Start time in ISO format
        :param end_time: End time in ISO format
        :param timezone: Timezone (default: UTC)
        :return: JSON response with signal counts
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"startTime": start_time, "endTime": end_time, "timezone": timezone}

        logger.info(f"Fetching signal counts from {start_time} to {end_time}")
        response = self.get("/signal-counts", params)
        return self._safe_json_parse(response, "get_signal_counts")

    def get_record_counts(self, start_time: str, end_time: str, timezone: str = "UTC"):
        """
        Get record counts for reporting volumes.

        :param start_time: Start time in ISO format
        :param end_time: End time in ISO format
        :param timezone: Timezone (default: UTC)
        :return: JSON response with record counts
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"startTime": start_time, "endTime": end_time, "timezone": timezone}

        logger.info(f"Fetching record counts from {start_time} to {end_time}")
        response = self.get("/record-counts", params)
        return self._safe_json_parse(response, "get_record_counts")

    # =================================================================
    # Network Blocks Endpoints
    # =================================================================

    def get_network_blocks(self, limit: int = 100, token: str = None):
        """
        Get all network blocks.

        :param limit: Maximum number of results to return
        :param token: Continuation token for pagination
        :return: JSON response with network blocks
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"limit": limit}
        if token:
            params["token"] = token

        logger.info("Fetching network blocks")
        response = self.get("/network-blocks", params)
        return self._safe_json_parse(response, "get_network_blocks")

    def get_network_block(self, block_id: str):
        """
        Get a specific network block by ID.

        :param block_id: The network block ID
        :return: JSON response with network block details
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info(f"Fetching network block: {block_id}")
        response = self.get(f"/network-blocks/{block_id}")
        return self._safe_json_parse(response, "get_network_block")

    # =================================================================
    # MITRE ATT&CK Endpoints
    # =================================================================

    def get_mitre_tactics(self, limit: int = 100, token: str = None):
        """
        Get all MITRE ATT&CK tactics.

        :param limit: Maximum number of results to return
        :param token: Continuation token for pagination
        :return: JSON response with MITRE tactics
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"limit": limit}
        if token:
            params["token"] = token

        logger.info("Fetching MITRE ATT&CK tactics")
        response = self.get("/mitre-tactics", params)
        return self._safe_json_parse(response, "get_mitre_tactics")

    def get_mitre_techniques(self, limit: int = 100, token: str = None):
        """
        Get all MITRE ATT&CK techniques.

        :param limit: Maximum number of results to return
        :param token: Continuation token for pagination
        :return: JSON response with MITRE techniques
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"limit": limit}
        if token:
            params["token"] = token

        logger.info("Fetching MITRE ATT&CK techniques")
        response = self.get("/mitre-techniques", params)
        return self._safe_json_parse(response, "get_mitre_techniques")

    # =================================================================
    # Signals Endpoints
    # =================================================================

    def get_signals(self, q: str = None, limit: int = 100, offset: int = 0):
        """
        Query signals using Cloud SIEM DSL.

        :param q: Query string in CSE DSL format (optional)
        :param limit: Maximum number of results to return
        :param offset: Starting offset for pagination
        :return: JSON response with signals
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"limit": limit, "offset": offset}
        if q:
            params["q"] = q

        logger.info(f"Querying signals with query: {q}")
        response = self.get("/signals", params)
        return self._safe_json_parse(response, "get_signals")

    def get_signal(self, signal_id: str):
        """
        Get a specific signal by ID.

        :param signal_id: The signal ID
        :return: JSON response with signal details
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info(f"Fetching signal: {signal_id}")
        response = self.get(f"/signals/{signal_id}")
        return self._safe_json_parse(response, "get_signal")

    # =================================================================
    # Suppressed Lists Endpoints
    # =================================================================

    def get_suppressed_lists(self, limit: int = 100, token: str = None):
        """
        Get all suppressed lists.

        :param limit: Maximum number of results to return
        :param token: Continuation token for pagination
        :return: JSON response with suppressed lists
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"limit": limit}
        if token:
            params["token"] = token

        logger.info("Fetching suppressed lists")
        response = self.get("/suppressed-lists", params)
        return self._safe_json_parse(response, "get_suppressed_lists")

    def get_suppressed_list(self, list_id: str):
        """
        Get a specific suppressed list by ID.

        :param list_id: The suppressed list ID
        :return: JSON response with suppressed list details
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info(f"Fetching suppressed list: {list_id}")
        response = self.get(f"/suppressed-lists/{list_id}")
        return self._safe_json_parse(response, "get_suppressed_list")

    # =================================================================
    # Threat Intelligence Endpoints
    # =================================================================

    def get_threat_intel_sources(self, limit: int = 100, token: str = None):
        """
        Get all threat intelligence sources.

        :param limit: Maximum number of results to return
        :param token: Continuation token for pagination
        :return: JSON response with threat intel sources
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"limit": limit}
        if token:
            params["token"] = token

        logger.info("Fetching threat intelligence sources")
        response = self.get("/threat-intel-sources", params)
        return self._safe_json_parse(response, "get_threat_intel_sources")

    def get_threat_intel_source(self, source_id: str):
        """
        Get a specific threat intelligence source by ID.

        :param source_id: The threat intel source ID
        :return: JSON response with threat intel source details
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info(f"Fetching threat intelligence source: {source_id}")
        response = self.get(f"/threat-intel-sources/{source_id}")
        return self._safe_json_parse(response, "get_threat_intel_source")

    def get_threat_intel_indicators(
        self, source_id: str, limit: int = 100, token: str = None
    ):
        """
        Get threat intelligence indicators for a specific source.

        :param source_id: The threat intel source ID
        :param limit: Maximum number of results to return
        :param token: Continuation token for pagination
        :return: JSON response with threat intel indicators
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"limit": limit}
        if token:
            params["token"] = token

        logger.info(f"Fetching threat intel indicators for source: {source_id}")
        response = self.get(f"/threat-intel-sources/{source_id}/indicators", params)
        return self._safe_json_parse(response, "get_threat_intel_indicators")

    # =================================================================
    # Tag Schemas Endpoints
    # =================================================================

    def get_tag_schemas(self, limit: int = 100, token: str = None):
        """
        Get all tag schemas.

        :param limit: Maximum number of results to return
        :param token: Continuation token for pagination
        :return: JSON response with tag schemas
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"limit": limit}
        if token:
            params["token"] = token

        logger.info("Fetching tag schemas")
        response = self.get("/tag-schemas", params)
        return self._safe_json_parse(response, "get_tag_schemas")

    def get_tag_schema(self, schema_id: str):
        """
        Get a specific tag schema by ID.

        :param schema_id: The tag schema ID
        :return: JSON response with tag schema details
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info(f"Fetching tag schema: {schema_id}")
        response = self.get(f"/tag-schemas/{schema_id}")
        return self._safe_json_parse(response, "get_tag_schema")

    # =================================================================
    # Rule Tuning Expressions Endpoints
    # =================================================================

    def get_rule_tuning_expressions(self, limit: int = 100, token: str = None):
        """
        Get all rule tuning expressions.

        :param limit: Maximum number of results to return
        :param token: Continuation token for pagination
        :return: JSON response with rule tuning expressions
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        params = {"limit": limit}
        if token:
            params["token"] = token

        logger.info("Fetching rule tuning expressions")
        response = self.get("/rule-tuning-expressions", params)
        return self._safe_json_parse(response, "get_rule_tuning_expressions")

    def get_rule_tuning_expression(self, expression_id: str):
        """
        Get a specific rule tuning expression by ID.

        :param expression_id: The rule tuning expression ID
        :return: JSON response with rule tuning expression details
        :raises APIError: If the API request fails
        :raises DataError: If response parsing fails
        """
        logger.info(f"Fetching rule tuning expression: {expression_id}")
        response = self.get(f"/rule-tuning-expressions/{expression_id}")
        return self._safe_json_parse(response, "get_rule_tuning_expression")
