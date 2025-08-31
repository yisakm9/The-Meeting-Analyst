# src/lambda_summarizer/index.py

import json
import urllib.parse
import boto3
import os
import uuid

print('Loading function')

s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')

# Get environment variables
OUTPUT_BUCKET = os.environ['OUTPUT_BUCKET_NAME']
TRANSCRIBE_ROLE_ARN = os.environ['TRANSCRIBE_ROLE_ARN'] # <-- NEW

def handler(event, context):
    """
    This function is triggered by SQS. It extracts the S3 object details
    and starts an asynchronous transcription job with Amazon Transcribe.
    """
    print("Received event: " + json.dumps(event, indent=2))

    for sqs_record in event['Records']:
        s3_event = json.loads(sqs_record['body'])

        if 'Records' in s3_event:
            for s3_record in s3_event['Records']:
                bucket = s3_record['s3']['bucket']['name']
                key = urllib.parse.unquote_plus(s3_record['s3']['object']['key'], encoding='utf-8')
                
                media_file_uri = f"s3://{bucket}/{key}"
                job_name = f"transcription-job-{uuid.uuid4()}" # Create a unique job name

                print(f"Starting transcription job '{job_name}' for file: {media_file_uri}")

                try:
                    # Make the API call to start the transcription job
                    transcribe.start_transcription_job(
                        TranscriptionJobName=job_name,
                        Media={'MediaFileUri': media_file_uri},
                        MediaFormat=key.split('.')[-1],  # Assumes format is in file extension (e.g., mp3)
                        LanguageCode='en-US', # Or make this configurable
                        OutputBucketName=OUTPUT_BUCKET,
                        OutputKey=f"transcripts/{job_name}.json", # Save transcripts in a subfolder
                        OutputAccessRole=TRANSCRIBE_ROLE_ARN # <-- ADD THIS LINE
                    )
                    print(f"Successfully started transcription job.")

                except Exception as e:
                    print(f"Error starting transcription job: {e}")
                    # Re-raise the exception to signal failure to SQS, allowing for retries
                    raise e
                    
    return {
        'statusCode': 200,
        'body': json.dumps('Transcription jobs started successfully')
    }