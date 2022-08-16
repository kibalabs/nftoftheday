

import base64
import hashlib
import json
import os
import re
from typing import Optional
import urllib.parse as urlparse

from core.requester import Requester
from core.exceptions import FoundRedirectException
from core.util import dict_util
from core.http.basic_authentication import BasicAuthentication

class TwitterAuthenticator:

    def __init__(self):
        self.requester = Requester()
        self.clientId = os.environ.get("TWITTER_OAUTH_CLIENT_ID")
        self.clientSecret = os.environ.get("TWITTER_OAUTH_CLIENT_SECRET")
        self.redirectUri = os.environ.get("TWITTER_OAUTH_REDIRECT_URI")
        self.tokenUrl = "https://api.twitter.com/2/oauth2/token"
        code_verifier = re.sub("[^a-zA-Z0-9]+", "", base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8"))
        code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
        self.code_challenge = code_challenge.replace("=", "")

    async def login(self, initialUrl: str, randomStateValue: str) -> None:
        state = {
            'initialUrl': initialUrl,
            'randomStateValue': randomStateValue,
        }
        stateString = base64.b64encode(json.dumps(state).encode()).decode()
        scopes = ['offline.access', 'tweet.read', 'tweet.write', 'users.read', 'follows.read', 'follows.write']
        params = {
            'response_type': 'code',
            'client_id': self.clientId,
            'redirect_uri': self.redirectUri,
            'scope': ' '.join(scopes),
            'code_challenge': self.code_challenge,
            'code_challenge_method': 'plain',
            'state': stateString,
        }
        raise FoundRedirectException(location=f'https://twitter.com/i/oauth2/authorize?{urlparse.urlencode(query=params, doseq=True, quote_via=urlparse.quote)}')

    async def login_callback(self, state: str, code: Optional[str], error: Optional[str]) -> None:
        stateDict = json.loads(base64.b64decode(state.encode()).decode())
        redirectQueryParams = {}
        if error:
            redirectQueryParams['error'] = error
        elif code:
            authHeader = BasicAuthentication(username=self.clientId, password=self.clientSecret)
            params = {
                'code': code,
                'grant_type': 'authorization_code',
                'client_id': self.clientId,
                'redirect_uri': self.redirectUri,
                'code_verifier': self.code_challenge,
            }
            response = await self.requester.post_form(url='https://api.twitter.com/2/oauth2/token', formDataDict=params, headers={'Authorization': f'Basic {authHeader.to_string()}'})
            responseDict = response.json()
            accessToken = responseDict['access_token']
            refreshToken = responseDict['refresh_token']
            # TODO(krishan711): save credentials
            redirectQueryParams = {
                'randomStateValue': stateDict['randomStateValue'],
            }
        else:
            redirectQueryParams['error'] = 'Response did not contain a code or error'
        urlParts = urlparse.urlparse(url=stateDict['initialUrl'])
        currentQuery = urlparse.parse_qs(urlParts.query)
        queryString = urlparse.urlencode(dict_util.merge_dicts(currentQuery, redirectQueryParams), doseq=True)
        url = urlparse.urlunsplit(components=(urlParts.scheme, urlParts.netloc, urlParts.path, queryString, urlParts.fragment))
        raise FoundRedirectException(location=url)
