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