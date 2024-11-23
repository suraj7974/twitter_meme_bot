import os
import tweepy
from dotenv import load_dotenv
import time
import json

load_dotenv()

class TwitterJobPoster:
    def __init__(self):
        """Initialize the Twitter Job Poster"""
        self.twitter_client = self._setup_twitter_client()

    def _setup_twitter_client(self):
        """Initialize Twitter API client"""
        try:
            client = tweepy.Client(
                bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
                consumer_key=os.getenv('TWITTER_API_KEY'),
                consumer_secret=os.getenv('TWITTER_API_SECRET_KEY'),
                access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
                access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            )
            return client
        except Exception as e:
            print(f"Twitter client setup error: {e}")
            return None

    def _format_job_tweet(self, job):
        """Format job details into a tweet"""
        try:
            tweet = (
                f"🚨 New Remote Job Alert! 🌐\n\n"
                f"Position: {job['title']}\n"
                f"\n🔗 Apply here: {job['link']}\n\n"
                f"#RemoteJob #JobAlert #RemoteWork"
            )
            return tweet if len(tweet) <= 280 else tweet[:277] + "..."
        except KeyError as e:
            print(f"Error formatting tweet - missing field: {e}")
            return None
        except Exception as e:
            print(f"Error formatting tweet: {e}")
            return None

    def post_jobs_to_twitter(self, jobs, max_jobs=5):
        """
        Post jobs to Twitter
        Returns the number of successfully posted jobs
        """
        if not self.twitter_client:
            print("Twitter client not initialized")
            return 0

        jobs_posted = 0
        
        for job in jobs[:max_jobs]:
            tweet_text = self._format_job_tweet(job)
            if tweet_text:
                try:
                    response = self.twitter_client.create_tweet(text=tweet_text)
                    print(f"Successfully posted job: {job['title']}")
                    jobs_posted += 1
                    
                    # Wait between tweets to avoid rate limits
                    if jobs_posted < max_jobs:
                        time.sleep(60)  
                except Exception as e:
                    print(f"Failed to post job: {e}")
                    continue

        return jobs_posted

def post_linkedin_jobs_to_twitter(json_file='linkedin_jobs.json', max_jobs=5):
    """
    Post LinkedIn jobs from JSON file to Twitter
    
    Args:
        json_file (str): Path to JSON file containing LinkedIn jobs
        max_jobs (int): Maximum number of jobs to post
    """
    try:
        # Load jobs from JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            jobs = data.get('jobs', [])

        if not jobs:
            print("No jobs found in JSON file")
            return

        # Initialize Twitter poster
        job_poster = TwitterJobPoster()
        if not job_poster.twitter_client:
            print("Failed to initialize Twitter client. Check your credentials.")
            return

        # Filter valid jobs (must have title and link)
        valid_jobs = [job for job in jobs if job.get('title') and job.get('link')]
        if not valid_jobs:
            print("No valid jobs to post")
            return

        # Post jobs
        print(f"Attempting to post {min(len(valid_jobs), max_jobs)} jobs to Twitter...")
        jobs_posted = job_poster.post_jobs_to_twitter(valid_jobs, max_jobs)
        print(f"Successfully posted {jobs_posted} jobs to Twitter")

    except FileNotFoundError:
        print(f"JSON file not found: {json_file}")
    except json.JSONDecodeError:
        print("Error decoding JSON file")
    except Exception as e:
        print(f"Error posting to Twitter: {str(e)}")

def test_twitter_connection():
    """Test Twitter API connection and credentials"""
    try:
        job_poster = TwitterJobPoster()
        if job_poster.twitter_client:
            test_tweet = "🧪 Test tweet - Checking Twitter API connection for job posting bot"
            response = job_poster.twitter_client.create_tweet(text=test_tweet)
            print("Twitter connection test successful!")
            return True
        else:
            print("Failed to initialize Twitter client")
            return False
    except Exception as e:
        print(f"Twitter connection test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # First test the connection
    if test_twitter_connection():
        # If connection is successful, post jobs
        post_linkedin_jobs_to_twitter()