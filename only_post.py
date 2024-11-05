import os
from groq import Groq
import tweepy
from dotenv import load_dotenv
import random

load_dotenv()


class TweetGenerator:
    def __init__(self):
        try:
            print("Initializing TweetGenerator...")
            self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            self._initialize_twitter()
            print("Initialization complete.")
        except Exception as e:
            print(f"Error during TweetGenerator initialization: {str(e)}")

    def _initialize_twitter(self):
        try:
            print("Initializing Twitter API credentials...")
            self.api_key = os.getenv('TWITTER_API_KEY')
            self.api_secret_key = os.getenv('TWITTER_API_SECRET_KEY')
            self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

            if not all([self.api_key, self.api_secret_key, self.access_token,
                        self.access_token_secret, self.bearer_token]):
                raise ValueError(
                    "Missing required Twitter API credentials in .env file")

            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret_key,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret
            )
            print("Twitter API initialized successfully.")
        except Exception as e:
            print(f"Error initializing Twitter API: {str(e)}")

    def generate_tweet_content(self):
        topics = [
            "resume optimization",
            "job interview tips",
            "tech career growth",
            "HR best practices",
            "workplace culture",
            "recruitment trends",
            "career development"
        ]

        selected_topic = random.choice(topics)
        print(f"Selected topic for tweet: {selected_topic}")

        prompt = f"""
        Write a short tweet about {selected_topic} in a Hinglish style. The tweet should be engaging and informative, mixing Hindi and English phrases
        written in Roman characters. It should be relatable for young professionals in India and include practical tips or insights.
        Keep the tweet under 240 characters and suggest 3-4 fresh, Hinglish-style hashtags to enhance reach.
        Format the response exactly like this:
        TWEET: [the tweet content]
        HASHTAGS: [hashtag1] [hashtag2] [hashtag3]
        """

        try:
            print("Generating tweet content via Groq API...")
            chat_completion = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-70b-versatile",
                temperature=0.7,
                max_tokens=200,
            )
            response = chat_completion.choices[0].message.content.strip()
            print("Tweet content generated successfully.")

            tweet_parts = response.split('\n')
            tweet_text = tweet_parts[0].replace('TWEET:', '').strip()
            hashtags = tweet_parts[1].replace('HASHTAGS:', '').strip()

            final_tweet = f"{tweet_text}\n\n{hashtags}"
            print(f"Generated tweet content:\n{final_tweet}")

            return final_tweet

        except Exception as e:
            print(f"Error generating tweet content: {str(e)}")
            return None

    def post_tweet(self):
        tweet_content = self.generate_tweet_content()

        if not tweet_content:
            print("Failed to generate tweet content")
            return False

        try:
            print("Posting tweet to Twitter...")
            response = self.client.create_tweet(text=tweet_content)
            tweet_id = response.data.get('id')
            if tweet_id:
                print(f"Tweet posted successfully! Tweet ID: {tweet_id}")
                return True
            else:
                print("Error: Twitter API did not return a tweet ID.")
                return False
        except Exception as e:
            print(f"Error posting tweet: {str(e)}")
            return False


def main():
    print("Starting tweet posting process...")
    tweet_gen = TweetGenerator()

    success = tweet_gen.post_tweet()

    if success:
        print("Tweet posting process completed successfully.")
    else:
        print("Tweet posting process failed.")


if __name__ == "__main__":
    main()
