# A Twitter Bot that tweet on schedule.

## Introduction

[Bamshi](https://twitter.com/Bamshi_The_Cat) is a Twitter bot designed to tweet random, weird facts about everything three times a day. It's an innovative way to engage with followers by sharing fun and interesting information in a delightful and automated manner. You can use the concept and workflow to create your bot.

## Setting Up

### Step 1: Creating a Twitter Developer Account

To use the Twitter API, you first need to create a Twitter Developer account. Here's how you can do it:

1. Go to the [Twitter Developer portal](https://developer.twitter.com/en).
2. Click on "Sign Up" and follow the instructions to create a developer account.
3. Once your account is set up, you have a project. Whitin the project create a new app to get your API keys and access tokens. Store your credential somewhere safe. You're gonna need only API (Consumer) Key and Secret and Access Token and Secret.

Note that on free tier of the Twitter Developer account you can just tweet.

### Step 2: Scraping Fun Facts

I scraped fun facts from the internet using Python scripts. Here's a brief overview:

- Use `requests` and `BeautifulSoup` to scrape web pages for facts.
- Extract and clean the data to fit Twitter's character limit.
- Save the cleaned facts in a text file for the bot to tweet.

Refer to the provided jupyter nb provided in repo (data_scraping.py) for detailed implementation.

### Step 3: Setting up AWS Services

[Bamshi](https://twitter.com/Bamshi_The_Cat) uses AWS services including Lambda, S3, and EventBridge. Make [AWS Free Tier account](https://aws.amazon.com/free) and then follow these steps:

1. **AWS Lambda**: On top left click on Services and in the search bar type `Lambda`. Click on Lambda (Run code without thinking about servers) and in the Lamvda page click on `Create function`. Choose `Author from scratch`, a proper `Function name` and select Python 3.9 as `Runtime`. Leave all the other option as default. Now you have a Lambda function that you can add layer (costume python environments and packages) or attach data bases and S3 buckets or new trigger to schedule the function.

2. **Custom Lambda Layers**: Creating a custom Lambda layer is to include the `tweepy` package and any other dependencies. For this, create a new folder on your machine like "tweepy_layer" and cd into it. Then use the bash command like below to create your stand-alone package inside a folder named `python`. It is important step and you should follow the name conventions. for this bot we need an environment that has `requests==2.25.0`, `beautifulsoup4`, `pytz` and `tweepy`. So:

```
pip install requests==2.25.0 -t ./python --no-user pip install beautifulsoup4 -t ./python --no-user pip install pytz -t ./python --no-user pip install tweepy -t ./python
```
Building the Fun Facts List as a Package inside costume layer: Create a package containing the `fun_facts.text` file and an `__init__.py` file that loads these facts into a list. Note that in your machine the file are in `tweepy_layer/python/funfacts/` but for lambda function the path would be `/opt/python/funfacts/`. So the `__init__.py` should include this path so you can import `fun_facts` inside the Lambda function:

```
fun_facts = []
with open('/opt/python/funfacts/fun_facts.txt', 'r') as file:
   for line in file:
       fun_facts.append(line.strip())
```

After creating all dependencies you can compress the folder as so:

```
zip -r ../tweepy_layer.zip .
```

Now if you go to Lambda -> Layers and click on `Create layer` you can upload your zip file and create your new costume layer. After creating your layer go to your function again (Lambda -> Functions -> Your_Func_Name) and at the very bottom of the page try to click on `Add a layer` and then choose your layer under `Custom layers`. Now your Lambda function can use the costume environment and the packages.

3. **Environment variables**: To keep sensitive information, like your Twitter API keys and tokens, secure we use environment variables instead of hard-coding the keys inside lambda function. Go to Lambda -> Functions -> Your_Func_Name and just above your `Code source` panel choose `Configuration` tab you can see `Environment variables` subsection and you have to add all of the twitter API credentials:
    - `CONSUMER_KEY` = your api key
    - `CONSUMER_SECRET` = your api key secret
    - `ACCESS_TOKEN` = your access token
    - `ACCESS_TOKEN_SECRET` = your access token secret

4. **S3**: To track the index of fun facts that bot tweet and strat from where it was left off we have to store the index of tweeted fact. Also we (optionally) will store tweet ids so we can delete them later if needed. For this I set up an S3 bucket for storing data like the current index and tweet IDs as simple json files:
    - current_index.json include just an integer which is our current fact index starting from 0.
    - tweet_ids.json is just an empty list [] and we will append the ids in it.

For this click on Services and in the search bar type `S3` and then `Create bucket` choose a propare `Bucket name` and leave everything as default. Then go Amazon S3 -> Buckets -> Your_Bucket_Name and upload two json files (current_index.json and tweet_ids.json).

To connect your Lambda function to your S3 bucket you should go to your Lambda function (Lambda -> Functions -> Your_Func_Name) and  just above your `Code source` panel choose `Configuration` tab you can see `Permissions` subsection you can find a link under Execution role -> Role name which you have to click. You'd be directed to a page (IAM -> Roles -> Your_Func_Role) where you can add new permissions. Under `Permissions policies` in the search bar write "S3Full" and select check box beside `AmazonS3FullAccess`. That's it. you granted your function a new pwrmission.

5. **EventBridge (CloudWatch Events)**: EventBridge is used to trigger the Lambda function at specific times (three times a day). The easiest way to do this is undet Lambda function page. So go to Lambda -> Functions -> Your_Func_Name and under `Function overview` click on `Add trigger`. In the new page in the `select a source` find `EventBridge (CloudWatch Events)` by writing it and then select `Create a new rule`. Write your Rule name and description. Under `Rule type` select `Schedule expression` and in the Schedule expression box follow this convention:

The schedule expression `cron(0 8,12,17 * * ? *)` is used in AWS, particularly with services like AWS Lambda and AWS CloudWatch, to define when a certain action should be triggered. It's a cron expression, which is a string representing a schedule in a time-based job scheduling format.

Here's a breakdown of this specific cron expression:

- `cron(0 8,12,17 * * ? *)`
  - `0`: The minute field. This specifies that the action should occur when the minute is `0`, i.e., at the top of the hour.
  - `8,12,17`: The hour field. This indicates that the action should occur at specific hours of the day, namely 8 AM, 12 PM, and 5 PM.
  - `*`: The day-of-month field. The asterisk signifies that the action should occur on every day of the month.
  - `*`: The month field. Similarly, an asterisk in this position signifies that the action should occur every month.
  - `?`: The day-of-week field. The question mark is used here to denote 'no specific value'. This is often used when the day-of-month is specified, to avoid conflicts or confusion between these two fields.
  - `*`: The year field. An asterisk here means every year.

Putting it all together, `cron(0 8,12,17 * * ? *)` means that the scheduled action should occur every day of every month of every year, specifically at 8:00 AM, 12:00 PM, and 5:00 PM.

## Lambda Function

The core of [Bamshi](https://twitter.com/Bamshi_The_Cat) is an AWS Lambda function written in Python. you should put this function in your Lamda function `Code source` in `lambda_function.py` file:

- Retrieves the current fact to be tweeted from the fun facts list.
- Uses `tweepy` to post the fact to Twitter.
- Updates the index and tweet IDs in the S3 bucket.

```
import os
import tweepy
import json
import boto3
from funfacts import fun_facts



consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
bearer = os.getenv("BEARER_TOKEN")


bucket_name = "bamshi-db"

index_file_key = 'current_index.json'
tweet_ids_file_key = 'tweet_ids.json'

# Initialize the AWS S3 Client
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    
    # Get the current index
    index_data = s3_client.get_object(Bucket=bucket_name, Key=index_file_key)
    current_index = json.load(index_data['Body'])
    
    if current_index > len(fun_facts):
        current_index = 0

    # Get the fun facts
    tweet_text = fun_facts[current_index]

    client = tweepy.Client(bearer_token=bearer,
                           consumer_key=consumer_key,
                           consumer_secret=consumer_secret,
                           access_token=access_token,
                           access_token_secret=access_token_secret)
    
    # Post the tweet
    response = client.create_tweet(text=tweet_text)
    tweet_id = response.data['id']
    
    # Update the tweet IDs list
    tweet_ids_data = s3_client.get_object(Bucket=bucket_name, Key=tweet_ids_file_key)
    tweet_ids = json.load(tweet_ids_data['Body'])
    tweet_ids.append(tweet_id)
    s3_client.put_object(Bucket=bucket_name, Key=tweet_ids_file_key, Body=json.dumps(tweet_ids))
    
    # Update and save the current index
    current_index = current_index + 1
    s3_client.put_object(Bucket=bucket_name, Key=index_file_key, Body=json.dumps(current_index))
```

## Deployment ant Test

Deploy your Lambda function and Test it in your main function page by clicking Deploy and Test under `Code source`.

## Conclusion

With these steps, [Bamshi](https://twitter.com/Bamshi_The_Cat) will be up and meowing out weird and fun facts to its Twitter audience. Enjoy engaging your followers with this unique and automated approach to social media!
