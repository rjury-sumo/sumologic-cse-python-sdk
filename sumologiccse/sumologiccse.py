import json
import requests
import os
import sys
import http.cookiejar as cookielib
import logging
import re

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=LOGLEVEL,
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger()


class SumoLogicCSE(object):
    def __init__(self, accessId=os.environ.get('SUMO_ACCESS_ID'),
                 accessKey=os.environ.get('SUMO_ACCESS_KEY'),
                 endpoint=None,
                 caBundle=None,
                 cookieFile='cookies.txt'):
        self.session = requests.Session()
        self.session.auth = (accessId, accessKey)
        self.DEFAULT_VERSION = 'v1'
        self.session.headers = {
            'content-type': 'application/json', 'accept': 'application/json'}
        if caBundle is not None:
            self.session.verify = caBundle
        cj = cookielib.FileCookieJar(cookieFile)
        self.session.cookies = cj
        if endpoint is None:
            self.endpoint = self._get_endpoint()
        elif re.match('au|fra|mum|us2|mon|dub|tky', endpoint):
            self.endpoint = 'https://api.' + endpoint + '.sumologic.com/api/sec'
        else:
            self.endpoint = endpoint
        if self.endpoint[-1:] == "/":
            raise Exception("Endpoint should not end with a slash character")
        logger.debug('endpoint: ' + str(self.endpoint))
        logger.debug('accessid: ' + accessId[0:3] + '####' + accessId[12:-1])

    def _get_endpoint(self):
        """
        SumoLogic REST API endpoint changes based on the geo location of the client.
        For example, If the client geolocation is Australia then the REST end point is
        https://api.au.sumologic.com/api/sec/v1

        When the default REST endpoint (https://api.sumologic.com/api/sec/v1) is used the server
        responds with a 401 and causes the SumoLogic class instantiation to fail and this very
        unhelpful message is shown 'Full authentication is required to access this resource'

        This method makes a request to the default REST endpoint and resolves the 401 to learn
        the right endpoint
        """

        self.endpoint = 'https://api.sumologic.com/api/sec'
        self.response = self.session.get(
            'https://api.sumologic.com/api/sec/v1/insights/all')  # Dummy call to get endpoint
        # dirty hack to sanitise URI and retain domain
        endpoint = self.response.url.replace('/v1/insights/all', '')
        print("SDK Endpoint", endpoint, file=sys.stderr)
        return endpoint

    def get_versioned_endpoint(self, version):
        return self.endpoint + '/%s' % version

    def delete(self, method, params=None, version=None):
        version = version or self.DEFAULT_VERSION
        endpoint = self.get_versioned_endpoint(version)
        r = self.session.delete(endpoint + method, params=params)
        if 400 <= r.status_code < 600:
            r.reason = r.text
        r.raise_for_status()
        return r

    def get(self, method, params=None, version=None):
        version = version or self.DEFAULT_VERSION
        endpoint = self.get_versioned_endpoint(version)
        r = self.session.get(endpoint + method, params=params)
        if 400 <= r.status_code < 600:
            r.reason = r.text
        r.raise_for_status()
        return r

    def post(self, method, params, headers=None, version=None):
        version = version or self.DEFAULT_VERSION
        endpoint = self.get_versioned_endpoint(version)
        r = self.session.post(
            endpoint + method, data=json.dumps(params), headers=headers)
        if 400 <= r.status_code < 600:
            r.reason = r.text
        r.raise_for_status()
        return r

    def post_file(self, method, params, headers=None, version=None):
        """
        Handle file uploads via a separate post request to avoid having to clear
        the content-type header in the session.

        Requests (or urllib3) does not set a boundary in the header if the content-type
        is already set to multipart/form-data.  Urllib will create a boundary but it
        won't be specified in the content-type header, producing invalid POST request.

        Multi-threaded applications using self.session may experience issues if we
        try to clear the content-type from the session.  Thus we don't re-use the
        session for the upload, rather we create a new one off session.
        """
        version = version or self.DEFAULT_VERSION
        endpoint = self.get_versioned_endpoint(version)
        post_params = {'merge': params['merge']}
        file_data = open(params['full_file_path'], 'rb').read()
        files = {'file': (params['file_name'], file_data)}
        r = requests.post(endpoint + method, files=files, params=post_params,
                          auth=(self.session.auth[0], self.session.auth[1]), headers=headers)
        if 400 <= r.status_code < 600:
            r.reason = r.text
        r.raise_for_status()
        return r

    def put(self, method, params, headers=None, version=None):
        version = version or self.DEFAULT_VERSION
        endpoint = self.get_versioned_endpoint(version)
        r = self.session.put(
            endpoint + method, data=json.dumps(params), headers=headers)
        if 400 <= r.status_code < 600:
            r.reason = r.text
        r.raise_for_status()
        return r

    # Insights
    # this is the raw call but can only returns up to 100 ['data']['objects']  and ['data']['nextPageToken']
    def get_insights_all(self, q=None, nextPageToken=None):
        params = {'q': q, 'nextPageToken': nextPageToken}
        response = self.get('/insights/all', params)
        return json.loads(response.text)

    # this handles pagination past 100 results
    # default max_pages will cap at 1000
    def get_insights(self, q=None, max_pages=10):
        insights = []
        pages = 0
        nextPageToken = None
        while pages < max_pages:
            pages += 1
            i = self.get_insights_all(q, nextPageToken)
            if len(i['data']['objects']) > 0:
                insights = insights + i['data']['objects']
            else:
                logger.debug("no results")

            nextPageToken = i['data']['nextPageToken']

            if nextPageToken == None:
                logger.debug(str(len(insights))
                             + ' insights at last page: ' + str(pages))
                break
        return insights

    def get_insight(self, insight_id):
        response = self.get('/insights/%s' % insight_id)
        return json.loads(response.text)

    def get_insight_statuses(self):
        response = self.get('/insight-status')
        return json.loads(response.text)

    def update_insight_resolution_status(self, insight_id, resolution, status):
        body = {'resolution': resolution, 'status': status}
        response = self.put('/insights/%s/status' % insight_id,body)
        return json.loads(response.text)

    def add_insight_comment(self, insight_id, comment):
        body = {'body': comment}
        response = self.post('/insights/%s/comments' % insight_id,body)
        return json.loads(response.text)
