# src/lambda_getter/index.py

import json
import boto3
import os

# Initialize outside the handler for reuse
DYNAMODB_TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

def handler(event, context):
    """
    This function is triggered by API Gateway to retrieve a single item
    from the DynamoDB table.
    """
    print(f"Received event: {json.dumps(event)}")

    # API Gateway passes path parameters in this structure
    try:
        meeting_id = event['pathParameters']['meetingId']
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'The path parameter "meetingId" is required.'})
        }

    print(f"Attempting to retrieve item with MeetingID: {meeting_id}")

    try:
        # Fetch the item from DynamoDB
        response = table.get_item(Key={'MeetingID': meeting_id})

        if 'Item' in response:
            print("Item found. Returning to client.")
            return {
                'statusCode': 200,
                # The response body must be a JSON string
                'body': json.dumps(response['Item'])
            }
        else:
            print("Item not found.")
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'Meeting with ID "{meeting_id}" not found.'})
            }

    except Exception as e:
        print(f"Error accessing DynamoDB: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'An internal server error occurred.'})
        }