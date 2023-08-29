from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build 
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
import base64
import openai
openai.api_key = ""

# If modifying these scopes, delete the file token.json.
SCOPES = [
    # "https://mail.google.com/", 
    # "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.readonly",
    # "https://www.googleapis.com/auth/gmail.metadata"
    ]

def get_subject_from_message(service, msg_id):
    try:
        msg = service.users().messages().get(userId='me', id=msg_id, format='metadata',
                                              metadataHeaders=['Subject']).execute()
        for header in msg['payload']['headers']:
            if header['name'] == 'Subject':
                return header['value']
        return "No Subject"
    except HttpError as error:
        print(f'An error occurred: {error}')

def get_yesterday_message_ids_and_senders(service):
    try:
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y/%m/%d')
        query = f'after:{yesterday}'
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q=query).execute()
        messages = results.get('messages', [])
        senders = []
        message_ids = []

        if not messages:
            print('No messages found.')
            return message_ids, senders

        for message in messages:
            msg_id = message['id']
            message_ids.append(msg_id)

            msg = service.users().messages().get(userId='me', id=msg_id, format='metadata',
                                                  metadataHeaders=['From']).execute()
            sender = msg['payload']['headers'][0]['value']
            senders.append(sender)

        return message_ids, senders

    except HttpError as error:
        print(f'An error occurred: {error}')

 

from bs4 import BeautifulSoup
import base64

def get_plain_text_from_message(message):
    if 'parts' in message['payload']:
        for part in message['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            elif part['mimeType'] == 'text/html':
                if 'data' in part['body']:
                    html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    soup = BeautifulSoup(html, 'html.parser')
                    return soup.get_text()
    elif 'body' in message['payload'] and 'data' in message['payload']['body']:
        return base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
    else:
        return "No message body found"

def summarize_email(service, msg_id):
    try:
        message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        msg_str = get_plain_text_from_message(message)
        
        if len(msg_str)>4000: msg_str=msg_str[:4000]
        # Summarize with GPT-4
        prompt = f"Summarize the following email content: {msg_str}"
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=50
        )
        return response.choices[0].text.strip()

    except HttpError as error:
        print(f'An error occurred: {error}')

def get_email_sentiment(text):
    prompt = f"What is the sentiment of this text: {text}"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=10
    )
    return response.choices[0].text.strip()

def get_email_urgency(text):
    prompt = f"How urgent is this email: {text}"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=10
    )
    return response.choices[0].text.strip()

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None

    df = pd.DataFrame(columns=['Sender', 'Subject', 'Summary', 'Sentiment', 'Urgency'])
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)

        # Fetch all message IDs from yesterday
        message_ids, senders = get_yesterday_message_ids_and_senders(service)

        if not message_ids:
            print("No message IDs found or an error occurred.")
        else:
            unique_senders = list(set(senders))  # Remove duplicates if any

            print(f"Unique Senders from Yesterday: {unique_senders}")

            for msg_id in message_ids:
                summarized_content = summarize_email(service, msg_id)
                subject = get_subject_from_message(service, msg_id)
                sender = "Unknown Sender"  # Replace this with the actual sender info
                sentiment = get_email_sentiment(summarized_content)
                urgency = get_email_urgency(summarized_content)
                
                df = df.append({
                    'Sender': sender, 
                    'Subject': subject, 
                    'Summary': summarized_content,
                    'Sentiment': sentiment,
                    'Urgency': urgency
                }, ignore_index=True)

            print(df)
            today = datetime.now() 
            df.to_csv(f"output/Daily_Digest_{today}.csv")
 
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()