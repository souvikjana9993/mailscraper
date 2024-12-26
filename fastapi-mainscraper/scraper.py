import os,json
import base64
from typing import Optional, List, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail() -> Credentials:
    """Authenticates with Gmail using OAuth 2.0 and returns credentials."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8070)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_emails_by_subject(email_id: str, subject_substring: str, max_results: Optional[int] = 10) -> List[
    Dict[str, Any]]:
    """
    Retrieves emails from Gmail that match the given subject substring.

    Args:
        email_id: The email address to search within.
        subject_substring: The substring to search for in the email subject.
        max_results: The maximum number of emails to retrieve.

    Returns:
        A list of dictionaries, where each dictionary represents an email
        containing the sender, subject, and a snippet of the body.
        Returns an empty list if no matching emails are found.
    """
    creds = authenticate_gmail()

    try:
        service = build('gmail', 'v1', credentials=creds)

        # Search for emails matching the subject substring
        query = f"subject:{subject_substring} to:{email_id}"
        results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages = results.get('messages', [])

        emails = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()

            # Extract headers (sender and subject)
            headers = msg['payload']['headers']
            sender = [header['value'] for header in headers if header['name'] == 'From'][0]
            subject = [header['value'] for header in headers if header['name'] == 'Subject'][0]

            # Decode body (snippet)
            if 'data' in msg['payload']['body']:
                data = msg['payload']['body']['data']
            else:
                data = msg['payload']['parts'][0]['body']['data']
            decoded_body = base64.urlsafe_b64decode(data).decode('utf-8')

            emails.append({
                'sender': sender,
                'subject': subject,
                'snippet': decoded_body + "...",  # Limit snippet length
            })

        # Store results in a JSON file
        output_filename = f"email_results_{email_id}_{subject_substring}.json"
        with open(output_filename, "w") as f:
            json.dump(emails, f, indent=4)  # Use indent for pretty printing

        return emails

    except HttpError as error:
        print(f"An error occurred: {error}")
        return []