# src/lambda_summarizer/index.py

import json
import urllib.parse
import boto3

print('Loading function')

s3 = boto3.client('s3')

def handler(event, context):
    """
    This function is triggered by an SQS message that contains an S3 event notification.
    It extracts the bucket name and object key from the event and prepares for processing.
    """
    print("Received event: " + json.dumps(event, indent=2))

    for sqs_record in event['Records']:
        # The actual S3 event notification is a JSON string inside the 'body' of the SQS message
        s3_event = json.loads(sqs_record['body'])

        if 'Records' in s3_event:
            for s3_record in s3_event['Records']:
                # Extract bucket and key from the S3 event record
                bucket = s3_record['s3']['bucket']['name']
                
                # The object key may have URL-encoded characters (e.g., spaces as '+')
                key = urllib.parse.unquote_plus(s3_record['s3']['object']['key'], encoding='utf-8')
                
                print(f"File found in S3: s3://{bucket}/{key}")

                # --- TODO ---
                # 1. Add logic to start an Amazon Transcribe job using the bucket and key.
                #    This will likely be an asynchronous call.
                #
                # 2. In a separate Lambda (triggered by a Transcribe job completion event),
                #    retrieve the transcript.
                #
                # 3. Send the transcript to Amazon Bedrock for summarization.
                #
                # 4. Store the transcript and summary in DynamoDB.
                #
                # 5. Send a notification via SNS.
                
    return {
        'statusCode': 200,
        'body': json.dumps('Processing started successfully')
    }