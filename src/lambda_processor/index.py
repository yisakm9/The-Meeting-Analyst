# src/lambda_processor/index.py

import json
import boto3
import urllib.parse
import os

print('Loading function')

s3 = boto3.client('s3')
transcribe = boto3.client('transcribe') # Add transcribe client

def handler(event, context):
    """
    This function is triggered by EventBridge when a Transcribe job is complete.
    It retrieves the job details, fetches the transcript, and prepares for summarization.
    """
    print("Received event: " + json.dumps(event, indent=2))

    # The job status is in the event, handle failures gracefully
    job_status = event['detail']['TranscriptionJobStatus']
    job_name = event['detail']['TranscriptionJobName']

    if job_status == 'FAILED':
        print(f"Transcription job '{job_name}' failed. Reason: {event['detail']['FailureReason']}")
        # You could send a notification here or just stop processing
        return

    if job_status == 'COMPLETED':
        print(f"Transcription job '{job_name}' completed successfully.")
        
        try:
            # *** FIX STARTS HERE ***
            # Make an API call to get the full job details
            job_details = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            
            # The transcript URI is located within the response object
            transcript_uri = job_details['TranscriptionJob']['Transcript']['TranscriptFileUri']
            # *** FIX ENDS HERE ***

            # The rest of the logic is the same as before
            parsed_uri = urllib.parse.urlparse(transcript_uri)
            bucket = parsed_uri.netloc
            key = parsed_uri.path.lstrip('/')

            print(f"Transcript for job '{job_name}' is located at: s3://{bucket}/{key}")

            response = s3.get_object(Bucket=bucket, Key=key)
            transcript_content = response['Body'].read().decode('utf-8')
            transcript_json = json.loads(transcript_content)
            
            full_transcript = transcript_json['results']['transcripts'][0]['transcript']
            
            print("--- Full Transcript ---")
            print(full_transcript)
            print("-----------------------")

            # --- TODO ---
            # 1. Send `full_transcript` to Bedrock.

        except Exception as e:
            print(f"Error processing transcript for job '{job_name}': {e}")
            raise e

    return {
        'statusCode': 200,
        'body': json.dumps(f"Successfully processed event for job: {job_name}")
    }