import json

# Load cookies from cookies.json
try:
    with open('cookies.json', 'r') as f:
        cookie_list = json.load(f)
        # Convert list of cookie objects to dictionary format
        cookie_data = {
            cookie['name']: cookie['value'] 
            for cookie in cookie_list 
            if cookie['domain'] in ['.twitter.com', '.x.com']  # Only get Twitter/X cookies
        }
        # Create cookie string directly from cookie_data
        cookie_string = '; '.join(f"{k}={v}" for k, v in cookie_data.items())
        # No need to parse cookie string back to dict since we already have cookie_data
        cookie_dict = cookie_data

except FileNotFoundError:
    print("Error: cookies.json not found. Please create this file with your Twitter cookies.")
    exit(1)

# Extract ct0 (CSRF token)
try:
    var_153625309350737955 = cookie_dict['ct0']
except KeyError:
    print("Error: 'ct0' token not found in cookies. This is required for authentication.")
    exit(1)

# Define fetch_and_parse_data
def fetch_and_parse_data(cookie_string):
    # For the purpose of this code, return hardcoded values
    result = {
        'var__2323771062872477764': 'twitter.com',
        'var_3178612813933597780': 'transaction123'
    }
    return result

# Call fetch_and_parse_data(cookie_string)
parameters = fetch_and_parse_data(cookie_string)

# Add var_153625309350737955 to parameters
parameters['var_153625309350737955'] = var_153625309350737955

# Now define create_tweet
def create_tweet(parameters, cookie_string):
    import requests
    url = 'https://' + parameters['var__2323771062872477764'] + '/i/api/graphql/znq7jUAqRjmPj7IszLem5Q/CreateTweet'
    headers = {
        'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
        'content-type': 'application/json',
        'origin': 'https://' + parameters['var__2323771062872477764'],
        'referer': 'https://twitter.com/home',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'priority': 'u=1, i',
        'x-client-transaction-id': parameters['var_3178612813933597780'],
        'x-csrf-token': parameters['var_153625309350737955'],
        'x-twitter-active-user': 'yes',
        'x-twitter-auth-type': 'OAuth2Session',
        'x-twitter-client-language': 'en',
        'cookie': cookie_string
    }
    data = {
        "variables": {
            "tweet_text": "Nice to meet you!",
            "dark_request": False,
            "media": {
                "media_entities": [],
                "possibly_sensitive": False
            },
            "semantic_annotation_ids": [],
            "disallowed_reply_options": None
        },
        "features": {
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
        },
        "queryId": "znq7jUAqRjmPj7IszLem5Q"
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        resp_json = response.json()
        rest_id = resp_json['data']['create_tweet']['tweet_results']['result']['rest_id']
        print(f"\n✅ Tweet posted successfully!")
        print(f"🔗 Tweet URL: https://twitter.com/i/web/status/{rest_id}")
        return {'rest_id': rest_id, 'success': True}
    except requests.exceptions.RequestException as e:
        error_msg = f"❌ Failed to post tweet: {str(e)}"
        if hasattr(e.response, 'json'):
            try:
                error_details = e.response.json()
                if 'errors' in error_details:
                    error_msg += f"\nAPI Error: {error_details['errors'][0]['message']}"
            except:
                pass
        print(f"\n{error_msg}")
        return {'rest_id': None, 'success': False, 'error': error_msg}

# Call create_tweet and handle the result
result = create_tweet(parameters, cookie_string)
if not result['success']:
    print("\n💡 Troubleshooting tips:")
    print("1. Check if your auth_token and ct0 cookies are valid")
    print("2. Make sure you're logged into Twitter")
    print("3. Try refreshing your cookies from the browser")
    print(result['error'])   