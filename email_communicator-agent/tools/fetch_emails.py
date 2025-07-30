#type: ignore
from agents import function_tool
import datetime
import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz
import re
import os
from dotenv import load_dotenv
load_dotenv()

Scopes = os.getenv('SCOPES')


@function_tool()
async def fetch_24_hours_email(email: str) -> str:
    """Fetch emails from the last 24 hours for the given Gmail address."""
    if not re.match(r'^[a-zA-Z0-9._%+-]+@(gmail|googlemail)\.com$', email):
        return f"Error: {email} is not a valid Gmail address. Please enter a Gmail address (e.g., user@gmail.com)."
    SCOPES = Scopes
    token_file = f"token_{email.replace('@', '_')}.pickle"
    creds = None

    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            try:
                creds = pickle.load(token)
            except Exception as e:
                return f"Error loading token file for {email}: {str(e)}"
    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    return "Error: credentials.json not found. Please download it from Google Cloud Console."
                print(f"\nAuthenticating for {email}...")
                print("A browser window will open to sign in with your Gmail account.")
                print("If you see 'Google hasn’t verified this app':")
                print("1. Click 'Advanced' at the bottom.")
                print("2. Click 'Go to EmailFetcherClient (unsafe)' to proceed.")
                print("This warning appears because the app is in testing mode, but it’s safe for you to use.")
                print(f"Please sign in with {email} to continue.\n")
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                service = build('gmail', 'v1', credentials=creds)
                profile = service.users().getProfile(userId='me').execute()
                authenticated_email = profile.get('emailAddress', '').lower()
                print(f"Authenticated as: {authenticated_email}")
                if authenticated_email != email.lower():
                    return f"Error: Authenticated account ({authenticated_email}) does not match requested email ({email}). Please sign in with {email}."
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
        except HttpError as e:
            if '403' in str(e):
                return (f"Error: Authentication failed for {email}. This email may not be added as a test user.\n"
                        "Please add it in Google Cloud Console:\n"
                        "1. Go to https://console.cloud.google.com > APIs & Services > OAuth consent screen.\n"
                        f"2. Under 'Test users,' add {email}.\n"
                        f"3. Delete {token_file} (if it exists) and try again.")
            return f"Error during authentication for {email}: {str(e)}. Did you cancel the authentication or encounter an error in the browser?"
        except Exception as e:
            return f"Error during authentication for {email}: {str(e)}. Did you cancel the authentication or encounter an error in the browser?"
    try:
        service = build('gmail', 'v1', credentials=creds)
    except Exception as e:
        return f"Error building Gmail service for {email}: {str(e)}"
    
    time_24_hours_ago = (datetime.datetime.now(pytz.UTC) - datetime.timedelta(hours=24)).strftime('%Y/%m/%d')
    query = f'from:* after:{time_24_hours_ago}'
    try:
        results = service.users().messages().list(userId='me', q=query, maxResults=10).execute()
        messages = results.get('messages', [])
        
        if not messages:
            return f"No emails found for {email} in the last 24 hours (checked up to {datetime.datetime.now(pytz.UTC)} UTC)."
        
        email_details = []
        for message in messages:
            try:
                msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                headers = msg.get('payload', {}).get('headers', [])
                subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), 'No Subject')
                sender = next((header['value'] for header in headers if header['name'].lower() == 'from'), 'Unknown Sender')
                date = next((header['value'] for header in headers if header['name'].lower() == 'date'), 'Unknown Date')
                snippet = msg.get('snippet', 'No Snippet Available')[:100] + '...' if len(msg.get('snippet', '')) > 100 else msg.get('snippet', 'No Snippet Available')
                email_details.append(f"From: {sender}\nSubject: {subject}\nDate: {date}\nSnippet: {snippet}\n{'-'*50}")
            except HttpError as e:
                email_details.append(f"Error fetching email {message['id']}: {str(e)}")
        
        return f"Fetched emails for {email} in the last 24 hours (checked up to {datetime.datetime.now(pytz.UTC)} UTC):\n\n" + "\n".join(email_details)
    
    except HttpError as e:
        return f"Error fetching emails for {email}: {str(e)}"
    except Exception as e:
        return f"Unexpected error fetching emails for {email}: {str(e)}"
