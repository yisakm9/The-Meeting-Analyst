# src/lambda_processor/index.py

import json
import boto3
from urllib.parse import urlparse

print('Loading function')

s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')
# --- ADDITION 1: Bedrock Runtime Client ---
# Use the 'bedrock-runtime' client for model invocation
bedrock_runtime = boto3.client('bedrock-runtime')

def handler(event, context):
    """
    This function is triggered by EventBridge, retrieves a transcript,
    sends it to Amazon Bedrock for summarization, and logs the result.
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
            https_uri = job_details['TranscriptionJob']['Transcript']['TranscriptFileUri']
            
            parsed_url = urlparse(https_uri)
            bucket = parsed_url.path.lstrip('/').split('/')[0]
            key = '/'.join(parsed_url.path.lstrip('/').split('/')[1:])
            
            print(f"Correctly parsed transcript location -> Bucket: [{bucket}], Key: [{key}]")

            response = s3.get_object(Bucket=bucket, Key=key)
            transcript_content = response['Body'].read().decode('utf-8')
            transcript_json = json.loads(transcript_content)
            
            full_transcript = transcript_json['results']['transcripts'][0]['transcript']
            
            print("--- Full Transcript Retrieved Successfully ---")
            # The '...' is removed because we will now process the full text.

            # ======================================================================
            # --- ADDITION 2: Bedrock Integration Logic ---
            # ======================================================================
            
            print("--- Sending transcript to Amazon Bedrock for summarization ---")
            
            # This is our prompt to the AI model. We are asking it to act as an assistant
            # and extract specific, structured information from the transcript.
            prompt = f"""
            Human: You are a helpful meeting assistant. Please analyze the following meeting transcript and provide a summary in three distinct sections:

            1.  **Summary:** A brief, one-paragraph summary of the meeting's purpose and key outcomes.
            2.  **Key Decisions:** A bulleted list of all major decisions that were made.
            3.  **Action Items:** A bulleted list of all specific action items, and who they were assigned to if mentioned.

            Here is the transcript:
            <transcript>
            {full_transcript}
            </transcript>

            Assistant:
            """

            # Structure the request body according to the model's requirements
            # (Claude 3 uses the "messages" format)
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt}]
                    }
                ]
            }

            # Invoke the model
            model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
            response = bedrock_runtime.invoke_model(
                body=json.dumps(request_body),
                contentType='application/json',
                accept='application/json',
                modelId=model_id
            )

            # Parse the response from the model
            response_body = json.loads(response.get('body').read())
            summary = response_body.get('content')[0].get('text')

            print("--- Bedrock Summary Received Successfully ---")
            print(summary)
            print("---------------------------------------------")

            # --- TODO ---
            # 1. Store the `full_transcript` and `summary` in DynamoDB.
            # 2. Send a notification via SNS containing the summary.

        except Exception as e:
            print(f"Error processing transcript for job '{job_name}': {e}")
            raise e

    return {
        'statusCode': 200,
        'body': json.dumps(f"Successfully processed and summarized job: {job_name}")
    }