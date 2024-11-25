## Set Up

```bash
python setup_scheduler.py
```

## Activate virtual env

For Linux or MacOs

```bash
source myenv/bin/activate
```

For Windows

```bash
myenv\Scripts\activate
```

## Set Up Groq API

Go to: https://console.groq.com/keys <br>
and create a api key and paste it in the .env file

## Set Up Twitter API

Go to: https://developer.x.com/en/portal/dashboard <br>  
Login using your Twitter account and then create a App then click on the key icon to generate keys. <br>

Make sure to create <br>
<b>API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, TWITTER_BEARER_TOKEN <br></b>
then paste all keys in .env file

## set trendy topics on trending_topics.json

Manually set the topics you want to use for meme in .json file

## To start

for posting the text post on twitter

```bash
python only_post.py
```

for posting meme on twitter

```bash
python main.py
```

# almighty-check
