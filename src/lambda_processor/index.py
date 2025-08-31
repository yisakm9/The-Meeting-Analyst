# src/lambda_processor/index.py

import json
import boto3

print('Loading function')

s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')

def handler(event, context):
    """
    This function is triggered by EventBridge when a Transcribe job is complete.
    It retrieves the job details, fetches the transcript, and prepares for summarization.
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
            
            # *** THE FIX IS HERE ***
            # Instead of parsing the complex URI, we use the direct fields from the API response.
            # This is far more reliable.
            transcript_reference = job_details['TranscriptionJob']['Transcript']
            
            # The API provides two ways to get the transcript. We prioritize the direct key.
            if 'RedactedTranscriptFileUri' in transcript_reference:
                # Handle redacted transcripts if you use that feature
                transcript_uri = transcript_reference['RedactedTranscriptFileUri']
            else:
                transcript_uri = transcript_reference['TranscriptFileUri']

            # Let's parse the URI robustly this time, by splitting
            # s3://bucket/key...
            parts = transcript_uri.replace("s3://", "").split("/", 1)
            bucket = parts[0]
            key = parts[1]
            
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