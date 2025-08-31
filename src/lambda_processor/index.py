# src/lambda_processor/index.py

import json
import boto3
from urllib.parse import urlparse
import os

print('Loading function')

s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')
bedrock_runtime = boto3.client('bedrock-runtime')
dynamodb = boto3.resource('dynamodb')
# --- ADDITION 1: SNS Client ---
sns = boto3.client('sns')

# Get Environment Variables
DYNAMODB_TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']
# --- ADDITION 2: Get SNS Topic ARN from Environment ---
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']


def handler(event, context):
    """
    This function is triggered by EventBridge, retrieves a transcript,
    sends it to Amazon Bedrock for summarization, stores the results in DynamoDB,
    sends a notification via SNS, and logs the result.
    """
    print("Received event: " + json.dumps(event, indent=2))

    job_status = event['detail']['TranscriptionJobStatus']
    job_name = event['detail']['TranscriptionJobName']

    if job_status == 'FAILED':
        print(f"Transcription job '{job_name}' failed. Reason: {event['detail'].get('FailureReason', 'Unknown')}")
        # Optionally, you could publish a failure notification to SNS here
        return

    if job_status == 'COMPLETED':
        print(f"Transcription job '{job_name}' completed successfully.")
        
        try:
            # ... (Logic to get transcript from S3 is unchanged) ...
            job_details = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            https_uri = job_details['TranscriptionJob']['Transcript']['TranscriptFileUri']
            parsed_url = urlparse(https_uri)
            bucket = parsed_url.path.lstrip('/').split('/')[0]
            key = '/'.join(parsed_url.path.lstrip('/').split('/')[1:])
            response = s3.get_object(Bucket=bucket, Key=key)
            transcript_content = response['Body'].read().decode('utf-8')
            transcript_json = json.loads(transcript_content)
            full_transcript = transcript_json['results']['transcripts'][0]['transcript']
            print("--- Transcript Retrieved Successfully ---")

            # ... (Logic to get summary from Bedrock is unchanged) ...
            prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>...""" # (prompt is the same)
            request_body = {"prompt": prompt, "max_gen_len": 2048, "temperature": 0.5, "top_p": 0.9}
            model_id = 'meta.llama3-70b-instruct-v1:0'
            response = bedrock_runtime.invoke_model(body=json.dumps(request_body), contentType='application/json', accept='application/json', modelId=model_id)
            response_body = json.loads(response.get('body').read())
            summary = response_body.get('generation')
            print("--- Bedrock Llama 3 Summary Received Successfully ---")

            # ... (Logic to store in DynamoDB is unchanged) ...
            table = dynamodb.Table(DYNAMODB_TABLE_NAME)
            item_to_store = {'MeetingID': job_name, 'Transcript': full_transcript, 'Summary': summary, 'SourceS3Key': key, 'SourceS3Bucket': bucket, 'ProcessingStatus': 'COMPLETED'}
            table.put_item(Item=item_to_store)
            print("--- Successfully wrote item to DynamoDB ---")

            # ======================================================================
            # --- ADDITION 3: SNS Integration Logic ---
            # ======================================================================
            
            print(f"--- Sending notification to SNS topic: {SNS_TOPIC_ARN} ---")
            
            # Create a user-friendly message for the notification.
            message_subject = f"Meeting Summary Ready: {job_name}"
            message_body = f"""
Hello,

The transcript and AI-powered summary for your meeting are now ready.

Meeting ID: {job_name}
Source File: s3://{bucket}/{key}

Summary Snippet:
---
{summary[:500]}... 
---

The full transcript and summary have been saved to the system for retrieval.
"""
            
            # Publish the message to the SNS topic
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=message_subject,
                Message=message_body
            )

            print("--- Successfully sent notification via SNS ---")

        except Exception as e:
            print(f"Error processing job '{job_name}': {e}")
            raise e

    return {
        'statusCode': 200,
        'body': json.dumps(f"Successfully processed, summarized, stored, and notified for job: {job_name}")
    }