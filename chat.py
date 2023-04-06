import openai
import os
import json
import boto3
from urllib.parse import unquote

def get_response(query):
    s3 = boto3.client('s3',
                      aws_access_key_id=os.environ['aws_access_key_id'],
                      aws_secret_access_key=os.environ['aws_secret_access_key'],
                      region_name='us-east-1')
    openai.api_key = os.environ['SECRET_KEY']
    
    message = s3.get_object(Bucket='chat-gpt-history', Key='history.txt')
    message_json = message['Body'].read().decode("utf-8")
    messages = json.loads(message_json)
    if len(messages) > 9 or query=='terminate':
        messages = [{"role": "user", "content": "hey"}]
    else:    
        messages.append({"role": "user", "content": '"'+ query + '"'})
    
    print(messages)
    completion = openai.ChatCompletion.create(model='gpt-3.5-turbo',messages=messages)
    
    response = completion['choices'][0]['message']['content']
    messages.append({"role": "assistant", "content": '"' + response + '"'})
    json_data = json.dumps(messages)
    s3.put_object(Bucket='chat-gpt-history', Key='history.txt', Body=json_data)
    return (completion['choices'][0]['message']['content'])
    
    
def lambda_handler(event, context):
    response = get_response(unquote(event['pathParameters']['query']))
    
    return {
        'statusCode': 200,
        'body': json.dumps(response.replace('\n', ''))
    }
