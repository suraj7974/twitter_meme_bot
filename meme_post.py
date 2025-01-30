import json
import time
import random
import os
from meme_generator import MemeGenerator
from media import TwitterPoster
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class HashtagGenerator:
    def __init__(self):
        try:
            print("Initializing HashtagGenerator...")
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError(
                    "GROQ_API_KEY environment variable not found.")
            self.groq_client = Groq(api_key=api_key)
            print("HashtagGenerator initialized successfully.")
        except Exception as e:
            print(f"Error initializing HashtagGenerator: {str(e)}")

    def generate_hashtags(self, topic, theme="career"):
        if isinstance(topic, dict):
            topic = topic.get('topic', '')

        print(f"Generating hashtags for topic: {topic} with theme: {theme}")

        prompt = f"""
        Generate 4-5 relevant hashtags for a social media post about '{topic}' related to {theme}.
        The hashtags should be:
        1. Relevant to careers, job search, and professional development
        2. Include at least one trending or popular hashtag
        3. Include one specific to the topic
        4. Be commonly used on social media
        
        Format the response as a single line of hashtags separated by spaces.
        Example format: #Career #JobTips #TechJobs
        """

        try:
            print("DEBUG: Sending request to Groq API...")
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-70b-versatile",
                temperature=0.6,
                max_tokens=100,
            )

            print(
                f"DEBUG: Raw response content: {response.choices[0].message.content}")

            try:
                content = response.choices[0].message.content
                if isinstance(content, str):
                    hashtags = content.strip()
                    formatted_hashtags = ' '.join(
                        ['#' + tag.lstrip('#') for tag in hashtags.split()])
                    print(f"Generated hashtags: {formatted_hashtags}")
                    return formatted_hashtags
                else:
                    print(
                        f"DEBUG: Content is not a string. Type: {type(content)}")
                    return "#JobSearch #CareerTips #ResumeBuilder"
            except AttributeError as e:
                print(f"DEBUG: Error accessing message content: {e}")
                return "#JobSearch #CareerTips #ResumeBuilder"

        except Exception as e:
            print(f"DEBUG: Exception in generate_hashtags: {str(e)}")
            print(f"DEBUG: Exception type: {type(e)}")
            return "#JobSearch #CareerTips #ResumeBuilder"


def generate_all_memes(meme_gen, hashtag_gen, trending_topics, company_theme):
    """Generate memes for all topics and return their paths with generated hashtags."""
    meme_data = []
    for article in trending_topics:  # Corrected to iterate over 'articles'
        try:
            print(f"Generating meme for topic: {article['title']}")
            topic = article['title']  # Using 'title' from the article dict

            meme_path = meme_gen.create_meme(topic, company_theme)

            if not meme_path:
                print(f"Failed to generate meme for topic: {topic}")
                continue

            hashtags = hashtag_gen.generate_hashtags(topic)
            meme_data.append({
                'topic': topic,
                'path': meme_path,
                'hashtags': hashtags
            })
            print(
                f"Meme generated and saved at: {meme_path} with hashtags: {hashtags}")
        except Exception as e:
            print(f"Error generating meme for topic '{article['title']}': {str(e)}")
    return meme_data


def post_random_meme(twitter, meme_data):
    """Select and post a random meme from the generated ones."""
    if not meme_data:
        print("No memes available to post!")
        return False

    try:
        selected_meme = random.choice(meme_data)
        topic = selected_meme['topic']
        meme_path = selected_meme['path']
        hashtags = selected_meme['hashtags']

        tweet_text = f"📈 {topic}\n\n{hashtags}"
        print(f"Posting meme for topic: {topic} with text: {tweet_text}")

        success = twitter.post_tweet(meme_path, tweet_text)

        if success:
            print(f"Successfully posted meme for topic: {topic}")
            meme_data.remove(selected_meme)
            try:
                os.remove(meme_path)
                print(f"Deleted used meme file: {meme_path}")
            except Exception as e:
                print(f"Error deleting meme file {meme_path}: {str(e)}")
        else:
            print(f"Failed to post meme for topic: {topic}")
        return success

    except Exception as e:
        print(f"Unexpected error while posting meme: {str(e)}")
        return False


def main():
    try:
        print("Starting meme generation process...")

        meme_gen = MemeGenerator()
        twitter = TwitterPoster()
        hashtag_gen = HashtagGenerator()
        company_theme = "Resume Building"

        try:
            with open('trending_tech_news.json', 'r') as f:
                data = json.load(f)
                trending_topics = data.get("articles", [])
                print("Loaded trending topics from file.")
            print("Random topics loaded from trending_topics.json file")
        except FileNotFoundError:
            print("trending_topics.json not found. Using sample topics...")
            trending_topics = [
                "Job Search 2024",
                "Remote Work",
                "AI in Workplace",
                "Career Growth",
                "Tech Skills"
            ]

        meme_data = generate_all_memes(
            meme_gen, hashtag_gen, trending_topics, company_theme)

        if not meme_data:
            print("No memes were generated successfully. Exiting...")
            return

        print(f"Generated {len(meme_data)} memes successfully")

        success = post_random_meme(twitter, meme_data)

        for meme in meme_data:
            try:
                os.remove(meme['path'])
                print(f"Cleaned up unused meme file: {meme['path']}")
            except Exception as e:
                print(f"Error cleaning up meme file {meme['path']}: {str(e)}")

        if success:
            print("Meme posting process completed successfully.")
        else:
            print("Meme posting process encountered issues.")

    except Exception as e:
        print(f"An unexpected error occurred in the main process: {str(e)}")


if __name__ == "__main__":
    main()
