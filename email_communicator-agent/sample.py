#type: ignore
from agents import Agent, Runner, function_tool
from config import config, model
import datetime
import os.path
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from email.mime.text import MIMEText
import base64
from typing import Union, Dict
import os
from dotenv import load_dotenv
load_dotenv()

Scopes = os.getenv('SCOPES')

@function_tool()
async def send_email(from_email: str, email: str, subject: str, body: str) -> Union[str, Dict[str, str]]:
    """Send an email from the specified Gmail address to the recipient with the given subject and body."""
    # Validate email formats
    if not re.match(r'^[a-zA-Z0-9._%+-]+@(gmail|googlemail)\.com$', from_email):
        return {"error": f"Invalid sender email: {from_email}. Must be a Gmail address."}
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return {"error": f"Invalid recipient email: {email}."}
    if not subject.strip():
        return {"error": "Subject cannot be empty."}
    if not body.strip():
        return {"error": "Body cannot be empty."}

    SCOPES = Scopes  # Supports both send and read
    token_file = f"token_{from_email.replace('@', '_')}.pickle"
    creds = None

    # Load existing credentials
    if os.path.exists(token_file):
        try:
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
            # Check if token has required scope
            if not any(scope in creds.scopes for scope in ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.modify']):
                print(f"Debug: Token for {from_email} lacks required scope. Re-authenticating...")
                creds = None  # Force re-authentication
        except Exception as e:
            return {"error": f"Error loading token file for {from_email}: {str(e)}"}
    else:
        print(f"Debug: No token file found for {from_email} at {token_file}")

    # Authenticate or refresh credentials
    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    return {"error": "credentials.json not found. Please download it from Google Cloud Console."}
                print(f"\nAuthenticating for {from_email}...")
                print("A browser window will open to sign in with your Gmail account.")
                print("If you see 'Google hasn’t verified this app':")
                print("1. Click 'Advanced' at the bottom.")
                print("2. Click 'Go to EmailFetcherClient (unsafe)' to proceed.")
                print("This warning appears because the app is in testing mode, but it’s safe for you to use.")
                print(f"Please sign in with {from_email} to continue.\n")
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                service = build('gmail', 'v1', credentials=creds)
                profile = service.users().getProfile(userId='me').execute()
                authenticated_email = profile.get('emailAddress', '').lower()
                print(f"Authenticated as: {authenticated_email}")
                if authenticated_email != from_email.lower():
                    return {"error": f"Authenticated account ({authenticated_email}) does not match sender email ({from_email}). Please sign in with {from_email}."}
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
        except HttpError as e:
            if '403' in str(e):
                return {"error": f"Authentication failed for {from_email}. This email may not be added as a test user.\n"
                                "Please add it in Google Cloud Console:\n"
                                "1. Go to https://console.cloud.google.com > APIs & Services > OAuth consent screen.\n"
                                f"2. Under 'Test users,' add {from_email}.\n"
                                f"3. Delete {token_file} (if it exists) and try again."}
            return {"error": f"Error during authentication for {from_email}: {str(e)}. Did you cancel the authentication or encounter an error in the browser?"}
        except Exception as e:
            return {"error": f"Error during authentication for {from_email}: {str(e)}. Did you cancel the authentication or encounter an error in the browser?"}
    
    # Build Gmail API service
    try:
        service = build('gmail', 'v1', credentials=creds)
    except Exception as e:
        return {"error": f"Error building Gmail service for {from_email}: {str(e)}"}
    
    # Create and send email
    try:
        # Create MIME message
        message = MIMEText(body)
        message['to'] = email
        message['from'] = from_email
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send email via Gmail API
        print(f"Debug: Sending email from {from_email} to {email} with subject '{subject}'")
        service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        print(f"Debug: Email sent successfully to {email}")
        return f"Email sent successfully to {email} with subject '{subject}'."
    except HttpError as e:
        return {"error": f"Error sending email to {email}: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error sending email to {email}: {str(e)}"}

async def main():
    send_emails_agent = Agent(
        name="send_email_agent",
        instructions="You are an email assistant. Send an email with the provided details and return the raw tool output without modification or mock data.",
        model=model,
        tools=[send_email],
        tool_use_behavior='stop_on_first_tool',
    )
    print("Welcome to the Email Assistant!")
    from_email = input("Enter the sender Gmail address: ").strip()
    to_email = input("Enter the recipient email address: ").strip()
    subject = input("Enter the email subject: ").strip()
    body = input("Enter the email body: ").strip()
    result = await Runner.run(
        starting_agent=send_emails_agent,
        input=f"send_email from '{from_email}' to '{to_email}' with subject '{subject}' and body '{body}'",
        run_config=config
    )
    
    print(result.final_output)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())