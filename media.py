import os
import tweepy
from dotenv import load_dotenv

load_dotenv()
class TwitterPoster:
    def __init__(self):
        try:
            print("Initializing TwitterPoster...")
            self._initialize_twitter()
            print("Initialization complete.")
        except Exception as e:
            print(f"Error during initialization: {str(e)}")

    def _initialize_twitter(self):
        try:
            print("Loading Twitter API credentials...")
            self.api_key = os.getenv('TWITTER_API_KEY')
            self.api_secret_key = os.getenv('TWITTER_API_SECRET_KEY')
            self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

            if not all([self.api_key, self.api_secret_key, self.access_token,
                        self.access_token_secret, self.bearer_token]):
                raise ValueError("Missing required Twitter API credentials in .env file")

            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret_key,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret
            )
            print("Twitter Client initialized successfully.")

            print("Initializing Twitter API v1.1 for media uploads...")
            auth = tweepy.OAuth1UserHandler(
                self.api_key,
                self.api_secret_key,
                self.access_token,
                self.access_token_secret
            )
            self.api = tweepy.API(auth)
            print("Twitter API v1.1 initialized successfully for media uploads.")

        except Exception as e:
            print(f"Error initializing Twitter API: {str(e)}")

    def post_tweet(self, image_path, tweet_text):
        try:
            print(f"Preparing to post tweet with image at {image_path} and text: '{tweet_text}'")

            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")

            print("Uploading media...")
            media = self.api.media_upload(image_path)
            print(f"Media uploaded successfully. Media ID: {media.media_id_string}")

            print("Posting tweet with media...")
            response = self.client.create_tweet(
                text=tweet_text,
                media_ids=[media.media_id_string]
            )

            tweet_id = response.data.get('id')
            if tweet_id:
                print(f"Tweet posted successfully! Tweet ID: {tweet_id}")
                return True
            else:
                print("Error: Tweet ID not returned in the response.")
                return False

        except FileNotFoundError as fnf_error:
            print(f"File error: {fnf_error}")
            return False
        except tweepy.errors.TweepyException as tw_error:
            print(f"Tweepy API error: {tw_error}")
            return False
        except Exception as e:
            print(f"Unexpected error posting to Twitter: {str(e)}")
            return False

if __name__ == "__main__":
    poster = TwitterPoster()

    poster.post_tweet("path/to/image.jpg", "Here's my latest update!")
