from twitter_sdk import TwitterAPI

# Initialize the API - clean and simple interface
twitter = TwitterAPI('cookies.json')

# Post a tweet
result = twitter.create_tweet("Hello from Twitter SDK!")

if result['success']:
    print(f"✅ Tweet posted successfully!")
    print(f"🔗 Tweet URL: {result['tweet_url']}")
else:
    print(f"❌ Failed to post tweet: {result['error']}") 