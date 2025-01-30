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
            "career development", "LinkedIn Optimization",
            "Soft Skills Development",
            "Networking Strategies",
            "Personal Branding",
            "Remote Work Tips",
            "Productivity Hacks",
            "Work-Life Balance",
            "Salary Negotiation Tips",
            "Freelancing & Gig Economy",
            "Entrepreneurship & Startups",
            "Workplace Diversity & Inclusion",
            "Time Management Techniques",
            "Leadership & Management Skills",
            "Emotional Intelligence at Work",
            "Mental Health in the Workplace",
            "Corporate Etiquette & Professionalism",
            "Team Collaboration Tips",
            "Learning & Upskilling",
            "Building a Strong Portfolio",
            "Career Change & Transition Strategies",
            "Job Search Strategies",
            "How to Stand Out in Job Applications",
            "Internship & Entry-Level Job Tips",
            "Handling Rejection & Career Setbacks",
            "Industry Insights & Trends Analysis",
            "interview mock round"
        ]

        selected_topic = random.choice(topics)
        print(f"Selected topic: {selected_topic}")

        prompt = f"""
        Generate a short tweet about {selected_topic} in a Hinglish style. The tweet should be engaging and informative, mixing Hindi and English phrases
        written in Roman characters. It should be relatable for young professionals in India and include practical tips or insights.
        Keep the tweet under 240 characters and suggest 3-4 fresh, Hinglish-style hashtags to enhance reach.
        
        The response MUST be in this EXACT format:
        TWEET: [Your tweet content in Hinglish, maximum 200 characters]
        HASHTAGS: #hashtag1 #hashtag2 #hashtag3
        
        Example format:
        TWEET: Job interview ke liye ready? Here's a pro tip: Always prepare 3 smart questions for the interviewer. Shows your seriousness!
        HASHTAGS: #JobInterview #CareerTips #InterviewPrep
        """

        try:
            print("Generating tweet content via Groq API...")
            chat_completion = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.2-3b-preview",
                temperature=0.7,
                max_tokens=200,
            )

            response = chat_completion.choices[0].message.content.strip()
            print(f"\nRaw response from Groq:\n{response}")

            # More robust parsing
            tweet_content = ""
            hashtags = ""

            lines = response.split('\n')
            for line in lines:
                if line.strip().startswith('TWEET:'):
                    tweet_content = line.replace('TWEET:', '').strip()
                elif line.strip().startswith('HASHTAGS:'):
                    hashtags = line.replace('HASHTAGS:', '').strip()

            if not tweet_content or not hashtags:
                print("Failed to parse tweet or hashtags properly")
                print(f"Tweet content: {tweet_content}")
                print(f"Hashtags: {hashtags}")
                return None

            final_tweet = f"{tweet_content}\n\n{hashtags}"
            if len(final_tweet) > 280:  # Twitter's character limit
                print("Generated tweet exceeds character limit")
                return None

            print(f"\nProcessed tweet:\n{final_tweet}")
            return final_tweet

        except Exception as e:
            print(f"Error generating tweet content: {str(e)}")
            print(f"Full error details:", e)
            return None

    def post_tweet(self):
        tweet_content = self.generate_tweet_content()

        if not tweet_content:
            print("Failed to generate tweet content")
            return False

        try:
            print("\nPosting tweet to Twitter...")
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
