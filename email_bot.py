# google API
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from api_keys import *

import email
import ssl
from imapclient import IMAPClient
from datetime import datetime, timedelta


class EmailBot:
    def __init__(self):
        # TODO: refactor for OAUTH2  https://developers.google.com/gmail/imap/xoauth2-protocol , https://stackoverflow.com/questions/5193707/use-imaplib-and-oauth-for-connection-with-gmail
        # IMAP lib docs https://imapclient.readthedocs.io/en/2.1.0/concepts.html#tls-ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        self.ssl_context = ssl_context

    def connect_for_user(self, user: str, passw: str):
        self.server = IMAPClient('imap.gmail.com', ssl_context=self.ssl_context)
        self.server.login(user, passw)
        inbox_selected = self.server.select_folder('INBOX')

    def get_emails_for_user(self, from_address: str = 'gattasb@gmail.com', last_n_days: int = 5):
        cutoff = datetime.today() - timedelta(days=last_n_days)
        messages = self.server.search(
            ['FROM "%s' % from_address, 'SINCE %s' % cutoff.strftime('%d-%b-%Y')])
        response = self.server.fetch(messages, ['RFC822'])

        for id, data in response.iteritems():
            msg_string = data['RFC822']
            msg = email.message_from_string(msg_string)
            print('IFrom: %s Date: %s' % (msg['From'], msg['date']))


# # EMAIL BOT TEST SCRIPT
# e = EmailBot()
# e.connect_for_user('z.miller9431@gmail.com', 'correspondence1')
# e.get_emails_for_user()


class OldEmailBot:
    def __init__(self, user: str, passw: str):
        # record api keys from constants file
        self.client_id = CLIENT_ID
        self.client_secret = SECRET
        self.connect_and_authenticate()
        # self.read_messages()

    def connect_and_authenticate(self):
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('gmail', 'v1', credentials=creds)
        msgs = service.users().messages().list(userId='me').execute()
        for msg in msgs['messages']:
            mid = msg['id']
            msgData = service.users().messages().get(userId='me', id=mid).execute()
            for header in msgData['payload']['headers']:
                if header['name'] == 'Subject':
                    subject = header['value']
                    print(subject)
                    break
            bodyText = msgData['payload']['body']

    #     # # Call the Gmail API
    #     results = service.users().labels().list(userId='me').execute()
    #     labels = results.get('labels', [])
    #     if not labels:
    #         print('No labels found.')
    #     else:
    #         print('Labels:')
    #         for label in labels:
    #             print(label['name'])
    # #
    # def read_messages(self):
    #     threads = self.service.users().threads().list(userId='me').execute().get('threads', [])
    #     for thread in threads:
    #         tdata = self.service.users().threads().get(userId='me', id=thread['id']).execute()
    #         nmsgs = len(tdata['messages'])
    #         msg = tdata['messages'][0]['payload']
    #         subject = ''
    #         for header in msg['headers']:
    #             if header['name'] == 'Subject':
    #                 subject = header['value']
    #                 break
    #             if subject: # skip if no Subject line
    #                 print('- %s (%d msgs)' % (subject, nmsgs))


