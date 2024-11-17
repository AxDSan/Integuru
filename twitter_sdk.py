import json
import requests
from typing import Dict
import os

class TwitterAPI:
    # Default feature flags required by Twitter's API
    DEFAULT_FEATURES = {
        'responsive_web_enhance_cards_enabled': True,
        'articles_preview_enabled': True,
        'rweb_video_timestamps_enabled': True,
        'tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled': True,
        'longform_notetweets_inline_media_enabled': True,
        'creator_subscriptions_quote_tweet_preview_enabled': True,
        'responsive_web_edit_tweet_api_enabled': True,
        'graphql_is_translatable_rweb_tweet_is_translatable_enabled': True,
        'standardized_nudges_misinfo': True,
        'freedom_of_speech_not_reach_fetch_enabled': True,
        'responsive_web_twitter_article_tweet_consumption_enabled': True,
        'longform_notetweets_rich_text_read_enabled': True,
        'tweet_awards_web_tipping_enabled': True,
        'longform_notetweets_consumption_enabled': True,
        'c9s_tweet_anatomy_moderator_badge_enabled': True,
        'rweb_tipjar_consumption_enabled': True,
        'view_counts_everywhere_api_enabled': True
    }

    def __init__(self, cookies_path: str):
        """Initialize the Twitter API client.
        
        Args:
            cookies_path: Path to the cookies.json file containing authentication cookies
        """
        self.base_url = "https://twitter.com/i/api/graphql"
        self.cookies = self._load_cookies(cookies_path)
        self.session = self._create_session()

    def _load_cookies(self, cookies_path: str) -> Dict:
        """Load cookies from the specified JSON file and format them properly.
        
        The cookies.json file typically contains an array of cookie objects from the browser.
        We need to convert this into a simple name:value dictionary.
        """
        try:
            with open(cookies_path, 'r') as f:
                cookies_data = json.load(f)
                
            # Convert the browser cookie format to a simple name:value dictionary
            cookie_dict = {}
            for cookie in cookies_data:
                if isinstance(cookie, dict) and 'name' in cookie and 'value' in cookie:
                    cookie_dict[cookie['name']] = cookie['value']
                
            if not cookie_dict:
                raise Exception("No valid cookies found in the cookies file")
                
            return cookie_dict
                
        except Exception as e:
            raise Exception(f"Failed to load cookies from {cookies_path}: {str(e)}")

    def _create_session(self) -> requests.Session:
        """Create and configure a requests session with necessary headers and cookies."""
        session = requests.Session()
        session.cookies.update(self.cookies)
        
        # Get CSRF token from cookies - Twitter uses 'ct0' as the CSRF token
        csrf_token = self.cookies.get('ct0')
        if not csrf_token:
            raise Exception("CSRF token (ct0) not found in cookies. Make sure your cookies.json is valid.")

        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'Content-Type': 'application/json',
            'X-Twitter-Active-User': 'yes',
            'X-Twitter-Client-Language': 'en',
            'x-csrf-token': csrf_token,  # Add CSRF token header
        })
        return session

    def create_tweet(self, text: str) -> Dict:
        """Create a new tweet."""
        try:
            query_id = "znq7jUAqRjmPj7IszLem5Q"
            
            variables = {
                "tweet_text": text,
                "dark_request": False,
                "media": {
                    "media_entities": [],
                    "possibly_sensitive": False
                },
                "semantic_annotation_ids": [],
                "disallowed_reply_options": None
            }

            # Match the working features exactly
            features = {
                "communities_web_enable_tweet_community_results_fetch": True,
                "c9s_tweet_anatomy_moderator_badge_enabled": True,
                "responsive_web_edit_tweet_api_enabled": True,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                "view_counts_everywhere_api_enabled": True,
                "longform_notetweets_consumption_enabled": True,
                "responsive_web_twitter_article_tweet_consumption_enabled": True,
                "tweet_awards_web_tipping_enabled": False,
                "creator_subscriptions_quote_tweet_preview_enabled": False,
                "longform_notetweets_rich_text_read_enabled": True,
                "longform_notetweets_inline_media_enabled": True,
                "articles_preview_enabled": True,
                "rweb_video_timestamps_enabled": True,
                "rweb_tipjar_consumption_enabled": True,
                "responsive_web_graphql_exclude_directive_enabled": True,
                "verified_phone_label_enabled": False,
                "freedom_of_speech_not_reach_fetch_enabled": True,
                "standardized_nudges_misinfo": True,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "responsive_web_graphql_timeline_navigation_enabled": True,
                "responsive_web_enhance_cards_enabled": False
            }

            payload = {
                "variables": variables,
                "features": features,
                "queryId": query_id
            }

            # Add transaction ID
            transaction_id = f"web-{hex(int.from_bytes(os.urandom(16), 'big'))}"
            
            # Update headers for this specific request
            self.session.headers.update({
                'origin': 'https://twitter.com',
                'referer': 'https://twitter.com/home',
                'priority': 'u=1, i',
                'x-client-transaction-id': transaction_id,
                'x-twitter-auth-type': 'OAuth2Session'
            })

            response = self.session.post(
                f"https://twitter.com/i/api/graphql/{query_id}/CreateTweet",
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                rest_id = data['data']['create_tweet']['tweet_results']['result']['rest_id']
                return {
                    'success': True,
                    'tweet_url': f"https://twitter.com/i/web/status/{rest_id}"
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def delete_tweet(self, tweet_id: str) -> Dict:
        """Delete a tweet.
        
        Args:
            tweet_id: The ID of the tweet to delete
            
        Returns:
            Dict containing success status and optional error message
        """
        try:
            operation_id = "DeleteTweet"
            
            variables = {
                "tweet_id": tweet_id,
                "dark_request": False
            }

            params = {
                "variables": json.dumps(variables),
                "features": json.dumps(self.DEFAULT_FEATURES)
            }

            response = self.session.post(
                f"{self.base_url}/{operation_id}",
                params=params
            )

            if response.status_code == 200:
                return {'success': True}
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            } 