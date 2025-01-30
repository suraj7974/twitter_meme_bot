## Install requirements

```bash
pip install -r requirements.txt
```

## Set Up env (in .env file)

GROQ_API_KEY=""

TWITTER_API_KEY=

TWITTER_API_SECRET_KEY=

TWITTER_ACCESS_TOKEN=

TWITTER_BEARER_TOKEN=

LINKEDIN_EMAIL=""

LINKEDIN_PASSWORD=""

## Install chrome & chrome driver (Both must of same version)

```bash
https://getwebdriver.com/chromedriver
```

### Add path of your chrome driver in chromedriver_setup.py

```bash
service = Service("/usr/bin/chromedriver")
```

## Scraping and posting jobs

for scraping jobs from linkedin

```bash
python scrape_linkedinjobs.py
```

for posting jobs to twitter

```bash
python job_post.py
```

## Meme

for scraping trending tech news

```bash
python scrape_trending_news.py
```

for posting meme on twitter

```bash
python meme_post.py
```

## Text post

for posting text post on twitter

```bash
python text_post.py
```
