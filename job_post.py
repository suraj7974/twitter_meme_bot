import os
import tweepy
from dotenv import load_dotenv
import time
import json
from datetime import datetime

load_dotenv()

class TwitterJobPoster:
    def __init__(self):
        """Initialize the Twitter Job Poster"""
        self.twitter_client = self._setup_twitter_client()
        self.posted_jobs_file = 'posted_jobs.json'
        self.posted_jobs = self._load_posted_jobs()

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

    def _load_posted_jobs(self):
        """Load previously posted jobs from JSON file"""
        try:
            if os.path.exists(self.posted_jobs_file):
                with open(self.posted_jobs_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {'posted_jobs': []}
        except Exception as e:
            print(f"Error loading posted jobs: {e}")
            return {'posted_jobs': []}

    def _save_posted_job(self, job, tweet_id):
        """Save posted job details to JSON file"""
        try:
            job_record = {
                'job_link': job['link'],
                'job_title': job['title'],
                'tweet_id': tweet_id,
                'posted_at': datetime.now().isoformat()
            }
            self.posted_jobs['posted_jobs'].append(job_record)
            
            with open(self.posted_jobs_file, 'w', encoding='utf-8') as f:
                json.dump(self.posted_jobs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving posted job: {e}")

    def is_job_posted(self, job_link):
        """Check if a job has already been posted"""
        return any(posted_job['job_link'] == job_link for posted_job in self.posted_jobs['posted_jobs'])

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
        Post jobs to Twitter, avoiding duplicates
        Returns the number of successfully posted jobs
        """
        if not self.twitter_client:
            print("Twitter client not initialized")
            return 0

        jobs_posted = 0
        
        # Filter out already posted jobs
        new_jobs = [job for job in jobs if not self.is_job_posted(job['link'])]
        
        if not new_jobs:
            print("No new jobs to post - all jobs have been posted already")
            return 0

        print(f"Found {len(new_jobs)} new jobs to post")
        
        for job in new_jobs[:max_jobs]:
            tweet_text = self._format_job_tweet(job)
            if tweet_text:
                try:
                    response = self.twitter_client.create_tweet(text=tweet_text)
                    tweet_id = response.data['id']
                    self._save_posted_job(job, tweet_id)
                    print(f"Successfully posted job: {job['title']}")
                    jobs_posted += 1
                    
                    # Wait between tweets to avoid rate limits
                    if jobs_posted < max_jobs:
                        time.sleep(60)  
                except Exception as e:
                    print(f"Failed to post job: {e}")
                    continue

        return jobs_posted

def post_linkedin_jobs_to_twitter(json_file='linkedin_jobs.json', max_jobs=1):
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
        print(f"Attempting to post up to {max_jobs} new jobs to Twitter...")
        jobs_posted = job_poster.post_jobs_to_twitter(valid_jobs, max_jobs)
        print(f"Successfully posted {jobs_posted} new jobs to Twitter")

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