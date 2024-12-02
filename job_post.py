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
        self.posted_jobs_file = "posted_jobs.json"
        self.posted_jobs = self._load_posted_jobs()

    def _setup_twitter_client(self):
        """Initialize Twitter API client"""
        try:
            client = tweepy.Client(
                bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
                consumer_key=os.getenv("TWITTER_API_KEY"),
                consumer_secret=os.getenv("TWITTER_API_SECRET_KEY"),
                access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
                access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
            )
            return client
        except Exception as e:
            print(f"Twitter client setup error: {e}")
            return None

    def _load_posted_jobs(self):
        """Load previously posted jobs from JSON file"""
        try:
            if os.path.exists(self.posted_jobs_file):
                with open(self.posted_jobs_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {"posted_jobs": []}
        except Exception as e:
            print(f"Error loading posted jobs: {e}")
            return {"posted_jobs": []}

    def _save_posted_job(self, job, tweet_id):
        """Save posted job details to JSON file"""
        try:
            job_record = {
                "job_link": job["link"],
                "job_title": job["title"],
                "company_name": job["company"],
                "tweet_id": tweet_id,
                "posted_at": datetime.now().isoformat(),
            }
            self.posted_jobs["posted_jobs"].append(job_record)

            with open(self.posted_jobs_file, "w", encoding="utf-8") as f:
                json.dump(self.posted_jobs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving posted job: {e}")

    def is_job_posted(self, job_link):
        """Check if a job has already been posted"""
        return any(
            posted_job["job_link"] == job_link
            for posted_job in self.posted_jobs["posted_jobs"]
        )

    def _format_job_tweet(self, job, job_number):
        """Format job details into a tweet"""
        try:
            tweet = (
                f"{job_number}. {job['title']}\n"
                f"Company: {job['company']}\n"
                f"{job['link']}"
            )
            return tweet
        except KeyError as e:
            print(f"Error formatting tweet - missing field: {e}")
            return None
        except Exception as e:
            print(f"Error formatting tweet: {e}")
            return None

    def post_jobs_to_twitter(self, jobs, max_jobs=5):
        """
        Post jobs to Twitter in a thread
        Returns the number of successfully posted jobs
        """
        if not self.twitter_client:
            print("Twitter client not initialized")
            return 0

        # Filter out already posted jobs
        new_jobs = [job for job in jobs if not self.is_job_posted(job["link"])]

        if not new_jobs:
            print("No new jobs to post - all jobs have been posted already")
            return 0

        print(f"Found {len(new_jobs)} new jobs to post")

        try:
            # Create the main tweet
            main_tweet_text = f"🚨 New Remote Job Postings! 🌐\n\nThread Below 👇"
            main_response = self.twitter_client.create_tweet(text=main_tweet_text)
            main_tweet_id = main_response.data["id"]
            
            # Post jobs as replies
            parent_tweet_id = main_tweet_id
            jobs_posted = 0

            for i, job in enumerate(new_jobs[:max_jobs], 1):
                tweet_text = self._format_job_tweet(job, i)
                
                if tweet_text:
                    try:
                        # Post each job as a reply to the previous tweet
                        reply_response = self.twitter_client.create_tweet(
                            text=tweet_text, 
                            in_reply_to_tweet_id=parent_tweet_id
                        )
                        
                        # Save the job as posted
                        self._save_posted_job(job, reply_response.data["id"])
                        
                        # Update parent tweet ID for next iteration
                        parent_tweet_id = reply_response.data["id"]
                        
                        jobs_posted += 1
                        print(f"Successfully posted job: {job['title']}")
                        
                        # Wait between tweets to avoid rate limits
                        time.sleep(30)
                        
                    except Exception as e:
                        print(f"Failed to post job: {e}")
                        continue

            return jobs_posted

        except Exception as e:
            print(f"Error creating tweet thread: {e}")
            return 0


def post_linkedin_jobs_to_twitter(json_file="linkedin_jobs.json", max_jobs=5):
    """
    Post LinkedIn jobs to Twitter
    :param json_file: Path to the JSON file containing jobs
    :param max_jobs: Maximum number of jobs to post in a single thread
    """
    try:
        # Load jobs from JSON file
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            jobs = data.get("jobs", [])

        if not jobs:
            print("No jobs found in JSON file")
            return

        # Initialize Twitter poster
        job_poster = TwitterJobPoster()
        if not job_poster.twitter_client:
            print("Failed to initialize Twitter client. Check your credentials.")
            return

        # Filter valid jobs (must have title, link, and company)
        valid_jobs = [
            job for job in jobs 
            if job.get("title") and job.get("link") and job.get("company")
        ]
        
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


if __name__ == "__main__":
    post_linkedin_jobs_to_twitter()