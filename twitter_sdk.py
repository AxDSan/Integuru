import json
import requests
from typing import Dict
import os
from playwright.async_api import async_playwright
import asyncio

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
        'view_counts_everywhere_api_enabled': True,
        "tweetypie_unmention_optimization_enabled": True,
        "responsive_web_graphql_skip_user_profile_image_extensions_enabled": True,
        "responsive_web_graphql_exclude_directive_enabled": True,
        "verified_phone_label_enabled": True,
        "communities_web_enable_tweet_community_results_fetch": True,
        "responsive_web_graphql_timeline_navigation_enabled": True
    }

    DEFAULT_AUTHORIZATION = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

    def __init__(self, cookies_path: str):
        """Initialize the Twitter API client.
        
        Args:
            cookies_path: Path to the cookies.json file containing authentication cookies
        """
        self.base_url = "https://twitter.com/i/api/graphql"
        self.cookies_path = cookies_path
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
            'Authorization': self.DEFAULT_AUTHORIZATION,
            'Content-Type': 'application/json',
            'X-Twitter-Active-User': 'yes',
            'X-Twitter-Client-Language': 'en',
            'x-csrf-token': csrf_token,
        })
        return session

    def create_tweet(self, tweet_text: str) -> Dict:
        """Create a new tweet with focused error handling"""
        try:
            url = f"{self.base_url}/znq7jUAqRjmPj7IszLem5Q/CreateTweet"
            
            headers = {
                'authorization': self.DEFAULT_AUTHORIZATION,
                'x-csrf-token': self.cookies['ct0'],
                'content-type': 'application/json',
            }

            data = {
                "variables": {
                    "tweet_text": tweet_text,
                    "dark_request": False,
                    "media": {
                        "media_entities": [],
                        "possibly_sensitive": False
                    },
                    "semantic_annotation_ids": []
                },
                "features": self.DEFAULT_FEATURES,
                "queryId": "znq7jUAqRjmPj7IszLem5Q"
            }

            response = self.session.post(url, json=data)
            response_json = response.json()

            # Handle API-specific error codes
            if 'errors' in response_json:
                error = response_json['errors'][0]
                error_code = error.get('code')
                error_msg = error.get('message', '')
                
                print(f"\n🚫 Twitter API Error {error_code}: {error_msg}")
                
                # Map common error codes
                ERROR_CODES = {
                    32: "Authentication error",
                    215: "Bad authentication data",
                    226: "Automation detected",
                    239: "Invalid authentication tokens"
                }
                
                if error_code in ERROR_CODES:
                    print(f"Known error type: {ERROR_CODES[error_code]}")
                
                return {
                    'success': False,
                    'error': f"API Error {error_code}: {error_msg}"
                }

            # Success case
            rest_id = response_json['data']['create_tweet']['tweet_results']['result']['rest_id']
            return {
                'success': True,
                'tweet_id': rest_id,
                'tweet_url': f"https://twitter.com/i/web/status/{rest_id}"
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Request failed: {str(e)}"
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

    async def refresh_auth(self, headless: bool = False) -> Dict:
        """Refresh authentication by launching a browser session"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)
            context = await browser.new_context()
            page = await context.new_page()
            
            await page.goto('https://twitter.com/home')
            print("Please log in to Twitter...")
            
            await page.wait_for_url("**/home", timeout=300000)
            
            cookies = await context.cookies()
            
            with open(self.cookies_path, 'w') as f:
                json.dump(cookies, f, indent=4)
            
            await browser.close()
            
            # Reload the session with new cookies
            self.cookies = self._load_cookies(self.cookies_path)
            self.session = self._create_session()
            
            print("✅ Authentication refreshed successfully!")
            return self.cookies

    async def ensure_auth(self) -> None:
        """Ensure valid authentication exists and is working, refresh if needed"""
        try:
            # First check if we have the required tokens
            if 'ct0' not in self.cookies or 'auth_token' not in self.cookies:
                print("Missing required authentication tokens. Refreshing...")
                await self.refresh_auth()
                return

            # Test authentication with a simple API call (e.g., fetch user settings)
            url = f"{self.base_url}/O5BMYyHKqQXyGnF5_ZjqLw/UserSettings"
            response = self.session.get(url)
            
            # Only refresh if we get specific authentication errors
            if response.status_code in [401, 403]:  # Unauthorized or Forbidden
                print("Authentication expired. Refreshing...")
                await self.refresh_auth()
            elif response.status_code != 200:
                print(f"Warning: API returned status {response.status_code}, but might still be valid")
                try:
                    error_json = response.json()
                    if any(error.get('code') in [32, 215, 239] for error in error_json.get('errors', [])):
                        # These are Twitter's specific auth error codes
                        print("Authentication invalid. Refreshing...")
                        await self.refresh_auth()
                except:
                    pass
            else:
                print("✅ Authentication valid!")
                
        except Exception as e:
            print(f"Error checking authentication: {str(e)}")
            # Only refresh if it's clearly an auth error
            if 'unauthorized' in str(e).lower() or 'forbidden' in str(e).lower():
                print("Refreshing authentication...")
                await self.refresh_auth() 