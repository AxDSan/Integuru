from twitter_sdk import TwitterAPI
import asyncio

async def main():
    try:
        twitter = TwitterAPI('cookies.json')
        await twitter.ensure_auth()

        tweet_text = "HOw you doing X!"
        print(f"\n📝 Posting tweet: '{tweet_text}'")
        
        result = twitter.create_tweet(tweet_text)

        if result['success']:
            print(f"\n✅ Tweet posted: {result['tweet_url']}")
        else:
            if 'authentication' in str(result['error']).lower():
                print("\n🔄 Refreshing authentication...")
                await twitter.refresh_auth()
                result = twitter.create_tweet(tweet_text)
                if result['success']:
                    print(f"\n✅ Tweet posted: {result['tweet_url']}")

    except Exception as e:
        print(f"\n💥 Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())