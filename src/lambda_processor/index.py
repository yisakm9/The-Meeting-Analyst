# src/lambda_processor/index.py

import json
import boto3
from urllib.parse import urlparse

print('Loading function')

s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')

def handler(event, context):
    """
    This function is triggered by EventBridge when a Transcribe job is complete.
    It retrieves the job details, correctly parses the S3 URI from the HTTPS URL,
    fetches the transcript, and prepares for summarization.
    """
    print("Received event: " + json.dumps(event, indent=2))

    job_status = event['detail']['TranscriptionJobStatus']
    job_name = event['detail']['TranscriptionJobName']

    if job_status == 'FAILED':
        print(f"Transcription job '{job_name}' failed. Reason: {event['detail'].get('FailureReason', 'Unknown')}")
        return

    if job_status == 'COMPLETED':
        print(f"Transcription job '{job_name}' completed successfully.")
        
        try:
            job_details = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            
            # The URI is a standard HTTPS URL, not an S3 URI.
            https_uri = job_details['TranscriptionJob']['Transcript']['TranscriptFileUri']
            
            # *** THE FIX IS HERE ***
            # We use urlparse to correctly break down the HTTPS URL.
            parsed_url = urlparse(https_uri)
            
            # The bucket name is the first part of the path, and the key is the rest.
            # Example path: /bucket-name/transcripts/job-name.json
            bucket = parsed_url.path.lstrip('/').split('/')[0]
            key = '/'.join(parsed_url.path.lstrip('/').split('/')[1:])
            
            print(f"Correctly parsed transcript location -> Bucket: [{bucket}], Key: [{key}]")

            response = s3.get_object(Bucket=bucket, Key=key)
            transcript_content = response['Body'].read().decode('utf-8')
            transcript_json = json.loads(transcript_content)
            
            full_transcript = transcript_json['results']['transcripts'][0]['transcript']
            
            print("--- Full Transcript Retrieved Successfully ---")
            print(full_transcript[:500] + "...") # Print first 500 chars

            # --- TODO: Bedrock Integration ---

        except Exception as e:
            print(f"Error processing transcript for job '{job_name}': {e}")
            raise e

    return {
        'statusCode': 200,
        'body': json.dumps(f"Successfully processed event for job: {job_name}")
    }