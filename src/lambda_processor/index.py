# src/lambda_processor/index.py

import json
import boto3
from urllib.parse import urlparse

print('Loading function')

s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')
bedrock_runtime = boto3.client('bedrock-runtime')

def handler(event, context):
    """
    This function is triggered by EventBridge, retrieves a transcript,
    sends it to Amazon Bedrock using the Llama 3 model for summarization,
    and logs the result.
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
            
            print(f"Retrieving transcript from Bucket: [{bucket}], Key: [{key}]")
            response = s3.get_object(Bucket=bucket, Key=key)
            transcript_content = response['Body'].read().decode('utf-8')
            transcript_json = json.loads(transcript_content)
            full_transcript = transcript_json['results']['transcripts'][0]['transcript']
            
            print("--- Transcript Retrieved Successfully ---")

            # ======================================================================
            # --- MODIFICATION: Bedrock Integration for Llama 3 ---
            # ======================================================================
            
            print("--- Sending transcript to Amazon Bedrock (Llama 3) for summarization ---")
            
            # Llama 3 uses a specific instruction format with special tokens.
            # We construct the prompt with system, user, and assistant roles.
            prompt = f"""
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a helpful meeting assistant. Your task is to analyze the meeting transcript provided by the user and create a summary with three specific sections: "Summary", "Key Decisions", and "Action Items". Format your entire response using Markdown.<|eot_id|><|start_header_id|>user<|end_header_id|>

Please analyze the following transcript and generate the summary as requested:
<transcript>
{full_transcript}
</transcript><|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""

            # Structure the request body according to the Llama 3 model's requirements
            request_body = {
                "prompt": prompt,
                "max_gen_len": 2048,  # Max tokens to generate
                "temperature": 0.5,   # Controls randomness. 0.5 is a good balance.
                "top_p": 0.9          # Nucleus sampling
            }

            # Invoke the Llama 3 model
            model_id = 'meta.llama3-70b-instruct-v1:0'
            response = bedrock_runtime.invoke_model(
                body=json.dumps(request_body),
                contentType='application/json',
                accept='application/json',
                modelId=model_id
            )

            # Parse the response from the Llama 3 model
            response_body = json.loads(response.get('body').read())
            summary = response_body.get('generation') # Llama 3's output is in the 'generation' key

            print("--- Bedrock Llama 3 Summary Received Successfully ---")
            print(summary)
            print("-----------------------------------------------------")

        except Exception as e:
            print(f"Error processing job '{job_name}': {e}")
            raise e

    return {
        'statusCode': 200,
        'body': json.dumps(f"Successfully processed and summarized job: {job_name}")
    }