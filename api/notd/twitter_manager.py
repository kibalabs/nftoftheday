import base64
import contextlib
import json
import os
import urllib.parse as urlparse
import uuid
from typing import Dict
from typing import List
from typing import Optional

from core.exceptions import FoundRedirectException
from core.exceptions import NotFoundException
from core.http.basic_authentication import BasicAuthentication
from core.queues.message_queue import MessageQueue
from core.queues.model import Message
from core.requester import Requester
from core.util import date_util
from core.util import dict_util
from core.util import list_util

from notd.messages import UpdateAllTwitterUsersMessageContent
from notd.model import RetrievedTwitterProfile
from notd.model import Signature
from notd.model import TwitterCredential
from notd.store.retriever import Retriever
from notd.store.saver import Saver


class TwitterManager:

    def __init__(self, saver: Saver, retriever: Retriever, requester: Requester, workQueue: MessageQueue[Message], twitterBearerToken: str):
        self.saver = saver
        self.retriever = retriever
        self.requester = requester
        self.workQueue = workQueue
        self.twitterBearerToken = twitterBearerToken
        self.clientId = os.environ["TWITTER_OAUTH_CLIENT_ID"]
        self.clientSecret = os.environ["TWITTER_OAUTH_CLIENT_SECRET"]
        self.redirectUri = os.environ["TWITTER_OAUTH_REDIRECT_URI"]
        self.tokenUrl = "https://api.twitter.com/2/oauth2/token"
        self.codeChallenge = str(uuid.uuid4())

    async def login(self, account: str, signature: Signature, initialUrl: str) -> None:
        userProfile = None
        with contextlib.suppress(NotFoundException):
            userProfile = await self.retriever.get_user_profile_by_address(address=account)
        if not userProfile:
            userProfile = await self.saver.create_user_profile(address=account, twitterId=None, discordId=None, signatureDict=signature.to_dict())
        state = {
            'account': account,
            'userProfileId': userProfile.userProfileId,
            'initialUrl': urlparse.unquote(initialUrl),
        }
        stateString = base64.b64encode(json.dumps(state).encode()).decode()
        scopes = ['offline.access', 'tweet.read', 'tweet.write', 'users.read', 'follows.read', 'follows.write']
        queryParams = {
            'response_type': 'code',
            'client_id': self.clientId,
            'redirect_uri': self.redirectUri,
            'scope': ' '.join(scopes),
            'code_challenge': self.codeChallenge,
            'code_challenge_method': 'plain',
            'state': stateString,
        }
        raise FoundRedirectException(location=f'https://twitter.com/i/oauth2/authorize?{urlparse.urlencode(query=queryParams, doseq=True, quote_via=urlparse.quote)}')

    async def login_callback(self, state: str, code: Optional[str], error: Optional[str]) -> None:
        stateDict = json.loads(base64.b64decode(state.encode()).decode())
        redirectQueryParams = {}
        if error:
            redirectQueryParams['error'] = error
        elif code:
            authHeader = BasicAuthentication(username=self.clientId, password=self.clientSecret)
            params: Dict[str, str] = {
                'code': code,
                'grant_type': 'authorization_code',
                'client_id': self.clientId,
                'redirect_uri': self.redirectUri,
                'code_verifier': self.codeChallenge,
            }
            response = await self.requester.post_form(url='https://api.twitter.com/2/oauth2/token', formDataDict=params, headers={'Authorization': f'Basic {authHeader.to_string()}'})
            responseDict = response.json()
            accessToken = responseDict['access_token']
            refreshToken = responseDict['refresh_token']
            expiryDate = date_util.datetime_from_now(seconds=responseDict['expires_in'])
            userResponse = await self.requester.get(url='https://api.twitter.com/2/users/me', headers={'Authorization': f'Bearer {accessToken}'})
            userResponseDict = userResponse.json()
            twitterId = userResponseDict['data']['id']
            userProfileId = stateDict['userProfileId']
            async with self.saver.create_transaction() as connection:
                userProfile = await self.retriever.get_user_profile(userProfileId=userProfileId, connection=connection)
                if not userProfile:
                    redirectQueryParams['error'] = 'User Profile Not Found'
                userProfile.twitterId = twitterId
                await self.saver.update_user_profile(userProfileId=userProfileId, twitterId=twitterId, connection=connection)
                twitterCredential = None
                with contextlib.suppress(NotFoundException):
                    twitterCredential = await self.retriever.get_twitter_credential_by_twitter_id(twitterId=twitterId)
                if not twitterCredential:
                    await self.saver.create_twitter_credential(twitterId=twitterId, accessToken=accessToken, refreshToken=refreshToken, expiryDate=expiryDate)
                else:
                    await self.saver.update_twitter_credential(twitterCredentialId=twitterCredential.twitterCredentialId, accessToken=accessToken, refreshToken=refreshToken, expiryDate=expiryDate)
            await self.update_twitter_profile(twitterId=twitterId)
        else:
            redirectQueryParams['error'] = 'Response did not contain a code or error'
        urlParts = urlparse.urlparse(url=stateDict['initialUrl'])
        currentQuery = urlparse.parse_qs(urlParts.query)
        queryString = urlparse.urlencode(dict_util.merge_dicts(currentQuery, redirectQueryParams), doseq=True)  # type: ignore[arg-type]
        url = urlparse.urlunsplit(components=(urlParts.scheme, urlParts.netloc, urlParts.path, queryString, urlParts.fragment))
        raise FoundRedirectException(location=url)

    async def refresh_twitter_credentials(self, twitterId: str) -> TwitterCredential:
        async with self.saver.create_transaction() as connection:
            twitterCredential = await self.retriever.get_twitter_credential_by_twitter_id(twitterId=twitterId, connection=connection)
            authHeader = BasicAuthentication(username=self.clientId, password=self.clientSecret)
            params: Dict[str, str] = {
                'refresh_token': twitterCredential.refreshToken,
                'grant_type': 'refresh_token',
                'client_id': self.clientId,
            }
            response = await self.requester.post_form(url='https://api.twitter.com/2/oauth2/token', formDataDict=params, headers={'Authorization': f'Basic {authHeader.to_string()}'})
            responseDict = response.json()
            twitterCredential.accessToken = responseDict['access_token']
            twitterCredential.refreshToken = responseDict['refresh_token']
            twitterCredential.expiryDate = date_util.datetime_from_now(seconds=responseDict['expires_in'])
            await self.saver.update_twitter_credential(twitterCredentialId=twitterCredential.twitterCredentialId, accessToken=twitterCredential.accessToken, refreshToken=twitterCredential.refreshToken, expiryDate=twitterCredential.expiryDate)
        return twitterCredential

    async def update_all_twitter_users_deferred(self) -> None:
        await self.workQueue.send_message(message=UpdateAllTwitterUsersMessageContent().to_message())

    async def update_all_twitter_users(self) -> None:
        allTwitterProfiles = await self.retriever.list_twitter_profiles()
        twitterIdProfileMap = {twitterProfile.twitterId: twitterProfile for twitterProfile in allTwitterProfiles}
        twitterIds = list(twitterIdProfileMap.keys())
        chunkedIds = list_util.generate_chunks(twitterIds, 100)
        for chunk in chunkedIds:
            ids = ','.join(chunk)
            dataDict = {
                'ids': ids,
                'expansions': 'pinned_tweet_id',
                'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld',
            }
            retrievedTwitterProfiles: List[RetrievedTwitterProfile] = []
            userResponse = await self.requester.get(url='https://api.twitter.com/2/users', dataDict=dataDict, headers={'Authorization': f'Bearer {self.twitterBearerToken}'})
            userResponseDict = userResponse.json()
            for userData in userResponseDict['data']:
                retrievedTwitterProfiles += [
                    RetrievedTwitterProfile(
                        username=userData['username'],
                        name=userData['name'],
                        description=userData['description'],
                        isVerified=userData['verified'],
                        pinnedTweetId=userData.get('pinned_tweet_id'),
                        followerCount=userData['public_metrics']['followers_count'],
                        followingCount=userData['public_metrics']['following_count'],
                        tweetCount=userData['public_metrics']['tweet_count'],
                        twitterId=userData['id'],
                    )
                ]
            for retrievedTwitterProfile in retrievedTwitterProfiles:
                twitterProfile = twitterIdProfileMap[retrievedTwitterProfile.twitterId]
                await self.saver.update_twitter_profile(twitterProfileId=twitterProfile.twitterProfileId, username=retrievedTwitterProfile.username, name=retrievedTwitterProfile.name, description=retrievedTwitterProfile.description, isVerified=retrievedTwitterProfile.isVerified, pinnedTweetId=retrievedTwitterProfile.pinnedTweetId, followerCount=retrievedTwitterProfile.followerCount, followingCount=retrievedTwitterProfile.followingCount, tweetCount=retrievedTwitterProfile.tweetCount)

    async def update_twitter_profile(self, twitterId: str) -> None:
        twitterCredential = await self.retriever.get_twitter_credential_by_twitter_id(twitterId=twitterId)
        if date_util.datetime_from_now(seconds=-60) > twitterCredential.expiryDate:
            twitterCredential = await self.refresh_twitter_credentials(twitterId=twitterId)
        twitterProfile = None
        with contextlib.suppress(NotFoundException):
            twitterProfile = await self.retriever.get_twitter_profile_by_twitter_id(twitterId=twitterId)
        dataDict = {
            'ids': twitterId,
            'expansions': 'pinned_tweet_id',
            'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld',
        }
        userResponse = await self.requester.get(url='https://api.twitter.com/2/users', dataDict=dataDict, headers={'Authorization': f'Bearer {twitterCredential.accessToken}'})
        userResponseDict = userResponse.json()
        username = userResponseDict['data'][0]['username']
        name = userResponseDict['data'][0]['name']
        description = userResponseDict['data'][0]['description']
        isVerified = userResponseDict['data'][0]['verified']
        pinnedTweetId = userResponseDict['data'][0].get('pinned_tweet_id')
        followerCount = userResponseDict['data'][0]['public_metrics']['followers_count']
        followingCount = userResponseDict['data'][0]['public_metrics']['following_count']
        tweetCount = userResponseDict['data'][0]['public_metrics']['tweet_count']
        if twitterProfile:
            await self.saver.update_twitter_profile(twitterProfileId=twitterProfile.twitterProfileId, username=username, name=name, description=description, isVerified=isVerified, pinnedTweetId=pinnedTweetId, followerCount=followerCount, followingCount=followingCount, tweetCount=tweetCount)
        else:
            await self.saver.create_twitter_profile(twitterId=twitterId, username=username, name=name, description=description, isVerified=isVerified, pinnedTweetId=pinnedTweetId, followerCount=followerCount, followingCount=followingCount, tweetCount=tweetCount)

    async def follow_user_from_user(self, userTwitterId: str, targetTwitterId: str) -> None:
        twitterCredential = await self.retriever.get_twitter_credential_by_twitter_id(twitterId=userTwitterId)
        if date_util.datetime_from_now(seconds=-60) > twitterCredential.expiryDate:
            twitterCredential = await self.refresh_twitter_credentials(twitterId=userTwitterId)
        dataDict = { 'target_user_id': targetTwitterId }
        await self.requester.post_json(url=f'https://api.twitter.com/2/users/{userTwitterId}/following', dataDict=dataDict, headers={'Authorization': f'Bearer {twitterCredential.accessToken}'})
