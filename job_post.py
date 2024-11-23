import os
import tweepy
from dotenv import load_dotenv
import time
import json
from datetime import datetime
import random

load_dotenv()

class TwitterJobPoster:
    def __init__(self):
        """Initialize the Twitter Job Poster"""
        self.twitter_client = self._setup_twitter_client()
        self.posted_jobs_file = 'posted_jobs_history.json'
        self.posted_jobs = self._load_posted_jobs()
        self.job_intros = [
            "🚨 Hot Remote Job Alert! 🌐",
            "💼 New Remote Opportunity! 🌍",
            "🎯 Just Posted: Remote Position 🚀",
            "📣 Remote Job Opening! ✨",
            "🌟 Fresh Remote Job Alert! 💻",
            "🔥 Latest Remote Opportunity! 🌎",
            "⚡️ New Remote Role Alert! 💪",
            "✨ Remote Position Available! 🎯",
        ]

    def _setup_twitter_client(self):
        """Initialize Twitter API client"""
        try:
            client = tweepy.Client(
                bearer_token=os.environ.get('TWITTER_BEARER_TOKEN'),
                consumer_key=os.environ.get('TWITTER_API_KEY'),
                consumer_secret=os.environ.get('TWITTER_API_SECRET_KEY'),
                access_token=os.environ.get('TWITTER_ACCESS_TOKEN'),
                access_token_secret=os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
            )
            return client
        except Exception as e:
            print(f"Twitter client setup error: {e}")
            return None

    def _load_posted_jobs(self):
        """Load history of posted jobs"""
        try:
            if os.path.exists(self.posted_jobs_file):
                with open(self.posted_jobs_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"posted_job_links": [], "last_update": None}
        except Exception as e:
            print(f"Error loading posted jobs history: {e}")
            return {"posted_job_links": [], "last_update": None}

    def _save_posted_jobs(self):
        """Save posted jobs history"""
        try:
            with open(self.posted_jobs_file, 'w', encoding='utf-8') as f:
                self.posted_jobs["last_update"] = datetime.now().isoformat()
                json.dump(self.posted_jobs, f, indent=2)
        except Exception as e:
            print(f"Error saving posted jobs history: {e}")

    def _format_job_tweet(self, job):
        """Format job details into a tweet with unique elements"""
        try:
            # Get current timestamp
            timestamp = datetime.now().strftime("%I:%M %p")
            
            # Get random intro
            intro = random.choice(self.job_intros)
            
            # Get random hashtags (mix and match from a pool)
            hashtag_pool = [
                "#RemoteWork", "#RemoteJob", "#JobAlert", "#JobSearch",
                "#WorkFromHome", "#WFH", "#RemoteWorking", "#JobOpening",
                "#Hiring", "#CareerOpportunity", "#JobHunt", "#RemoteLife"
            ]
            selected_hashtags = random.sample(hashtag_pool, 3)
            hashtag_string = " ".join(selected_hashtags)

            tweet = (
                f"{intro}\n\n"
                f"🎯 {job['title']}\n\n"
                f"🔗 Apply now: {job['link']}\n\n"
                f"{hashtag_string}\n"
                f"Posted at {timestamp} ET"
            )
            return tweet if len(tweet) <= 280 else tweet[:277] + "..."
        except KeyError as e:
            print(f"Error formatting tweet - missing field: {e}")
            return None
        except Exception as e:
            print(f"Error formatting tweet: {e}")
            return None

    def is_job_posted(self, job_link):
        """Check if a job has already been posted"""
        return job_link in self.posted_jobs["posted_job_links"]

    def mark_job_as_posted(self, job_link):
        """Mark a job as posted"""
        if job_link not in self.posted_jobs["posted_job_links"]:
            self.posted_jobs["posted_job_links"].append(job_link)
            self._save_posted_jobs()

    def get_next_unposted_job(self, jobs):
        """Get the next unposted job"""
        for job in jobs:
            if not self.is_job_posted(job['link']):
                return job
        return None

    def post_single_job(self, jobs):
        """
        Post a single unposted job to Twitter
        Returns True if successful, False otherwise
        """
        if not self.twitter_client:
            print("Twitter client not initialized")
            return False

        next_job = self.get_next_unposted_job(jobs)
        
        if not next_job:
            print("No new jobs to post")
            return False

        tweet_text = self._format_job_tweet(next_job)
        if tweet_text:
            try:
                response = self.twitter_client.create_tweet(text=tweet_text)
                print(f"Successfully posted job: {next_job['title']}")
                self.mark_job_as_posted(next_job['link'])
                return True
            except Exception as e:
                print(f"Failed to post job: {e}")
                return False
        return False

def post_linkedin_job_to_twitter(json_file='linkedin_jobs.json'):
    """
    Post a single LinkedIn job from JSON file to Twitter
    """
    try:
        # Load jobs from JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            jobs = data.get('jobs', [])

        if not jobs:
            print("No jobs found in JSON file")
            return False

        # Initialize Twitter poster
        job_poster = TwitterJobPoster()
        if not job_poster.twitter_client:
            print("Failed to initialize Twitter client. Check your credentials.")
            return False

        # Filter valid jobs (must have title and link)
        valid_jobs = [job for job in jobs if job.get('title') and job.get('link')]
        if not valid_jobs:
            print("No valid jobs to post")
            return False

        # Post single job
        success = job_poster.post_single_job(valid_jobs)
        return success

    except FileNotFoundError:
        print(f"JSON file not found: {json_file}")
        return False
    except json.JSONDecodeError:
        print("Error decoding JSON file")
        return False
    except Exception as e:
        print(f"Error posting to Twitter: {str(e)}")
        return False

if __name__ == "__main__":
    success = post_linkedin_job_to_twitter()
    # For GitHub Actions, exit with appropriate status code
    exit(0 if success else 1)