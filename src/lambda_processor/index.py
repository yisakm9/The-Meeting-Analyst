# src/lambda_processor/index.py

import json
import boto3
import urllib.parse
import os

print('Loading function')

s3 = boto3.client('s3')

# Get environment variables (will be used in later steps)
# DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE_NAME']
# SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def handler(event, context):
    """
    This function is triggered by an EventBridge rule when a Transcribe job is complete.
    It retrieves the transcript, and will eventually send it to Bedrock.
    """
    print("Received event: " + json.dumps(event, indent=2))

    # EventBridge event 'detail' contains information about the completed job
    job_name = event['detail']['TranscriptionJobName']
    
    # The transcript file location is provided in the event
    transcript_uri = event['detail']['Transcript']['TranscriptFileUri']
    
    # The URI is in the format: "s3://bucket-name/path/to/transcript.json"
    # We need to parse the bucket and key from this URI
    parsed_uri = urllib.parse.urlparse(transcript_uri)
    bucket = parsed_uri.netloc
    key = parsed_uri.path.lstrip('/') # Remove leading '/'

    print(f"Transcript for job '{job_name}' is located at: s3://{bucket}/{key}")

    try:
        # Fetch the transcript file from S3
        response = s3.get_object(Bucket=bucket, Key=key)
        transcript_content = response['Body'].read().decode('utf-8')
        
        # The content is a large JSON object from Transcribe
        transcript_json = json.loads(transcript_content)
        
        # Extract the actual transcript text
        full_transcript = transcript_json['results']['transcripts'][0]['transcript']
        
        print("--- Full Transcript ---")
        print(full_transcript)
        print("-----------------------")

        # --- TODO ---
        # 1. Send the `full_transcript` text to Amazon Bedrock for summarization.
        # 2. Store the transcript and summary in DynamoDB.
        # 3. Send a notification via SNS.

    except Exception as e:
        print(f"Error processing transcript from S3: {e}")
        raise e

    return {
        'statusCode': 200,
        'body': json.dumps(f"Successfully processed transcript for job: {job_name}")
    }