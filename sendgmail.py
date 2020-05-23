#!/usr/bin/python
from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import os
import json

from apiclient import errors

from sys import stdin
from sys import argv
import sys

import argparse

"""Send an email message from the user's account.
"""


def create_message(sender, to, cc, bcc, subject, message_text):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    message['bcc'] = bcc
    message['cc'] = cc
    rawmsg = {'raw': base64.urlsafe_b64encode(
        message.as_string().encode('utf-8')).decode('utf-8')}
    # base64_bytes = b64encode(byte_content)
    # # third: decode these bytes to text
    # # result: string (in utf-8)
    # base64_string = base64_bytes.decode(ENCODING)
    # print (rawmsg)
    return rawmsg
    # TypeError: a bytes-like object is required, not 'str'


def create_draft(service, user_id, message_body):
    """Create and insert a draft email. Print the returned draft's message and id.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      message_body: The body of the email message, including headers.

    Returns:
      Draft object, including draft id and message meta data.
    """
    try:
        message = {'message': message_body}
        draft = service.users().drafts().create(userId=user_id, body=message).execute()

        print('Draft id: %s\nDraft message: %s' %
              (draft['id'], draft['message']))

        return draft
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
        return None


def create_message_with_attachment(
        sender, to, cc, bcc, subject, message_text, files):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.
      file: The path to the file to be attached.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['cc'] = cc
    message['bcc'] = bcc
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    for file in files:
        content_type, encoding = mimetypes.guess_type(file)
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        if main_type == 'text':
            fp = open(file, 'r')
            msg = MIMEText(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'image':
            fp = open(file, 'rb')
            msg = MIMEImage(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'audio':
            fp = open(file, 'rb')
            msg = MIMEAudio(fp.read(), _subtype=sub_type)
            fp.close()
        else:
            fp = open(file, 'rb')
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
            fp.close()
        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)
    #  return {'raw': base64.urlsafe_b64encode(message.as_string())}
    return {'raw': base64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode('utf-8')}


def send_message(service, user_id, message):
    """Send an email message.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      message: Message to be sent.

    Returns:
      Sent Message.
    """
    try:
        # print(message)
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send']


def main(args):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    credentialsjson = args.credentials
    if not credentialsjson and os.path.exists('./credentials.json'):
        credentialsjson = './credentials.json'
    else:
        credentialsjson = os.path.join(
            os.environ['HOME'], '.config', 'sendgmail', 'credentials.json')

    tokenpickle = args.token
    if not tokenpickle and os.path.exists('./token.pickle'):
        tokenpickle = './token.pickle'
    else:
        tokenpickle = os.path.join(
            os.environ['HOME'], '.config', 'sendgmail', 'token.pickle')

    if os.path.exists(tokenpickle):
        with open(tokenpickle, 'rb') as token:
            creds = pickle.load(token, encoding='latin1')

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentialsjson, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(tokenpickle, 'wb') as token:
            pickle.dump(creds, token)
            # ^^^ may need changing.

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    mtext = args.message
    if args.file:
        with open(args.file, 'r') as f:
            mtext = f.read()

    # This is not trivial to detect if data is coming from pipe
    # if stdin:
    #     mtext = ''
    #     for line in stdin:
    #         mtext = mtext + line

    subject = args.subject
    to = args.to
    send_from = args.sender
    cc = args.cc
    bcc = args.bcc
#    subject = "Engagement tracker: " + subject

    if args.attach:
        mymessage = create_message_with_attachment(
            send_from, to, cc, bcc, subject, mtext, args.attach)
    else:
        mymessage = create_message(send_from, to, cc, bcc, subject, mtext)
    send_message(service, send_from, mymessage)


parser = argparse.ArgumentParser(description='Send gmail command line utility')
parser.add_argument('--to', action='store')
parser.add_argument('--sender', action='store')
parser.add_argument('--cc', action='store')
parser.add_argument('--bcc', action='store')
parser.add_argument('--subject', action='store')
parser.add_argument('--message', action='store')
parser.add_argument('--file', action='store')
parser.add_argument('--credentials', action='store')
parser.add_argument('--token', action='store')
parser.add_argument('--attach', nargs='*')
parser.add_argument('--configuration', action='store')

args = parser.parse_args()

# configuration is given a higher priority then command line
# this can be changed if needed
configuration = args.configuration
fallback_config = os.path.join(
    os.environ['HOME'], '.config', 'sendgmail', 'config.json')

if not configuration:
    if os.path.exists('config.json'):
        configuration = 'config.json'
    elif os.path.exists(fallback_config):
        configuration = fallback_config

if configuration:
    with open(configuration, 'r') as f:
        config = json.load(f)
        args.to = config['to'] if 'to' in config else args.to
        args.sender = config['sender'] if 'sender' in config else args.sender
        args.cc = config['cc'] if 'cc' in config else args.cc
        args.bcc = config['bcc'] if 'bcc' in config else args.bcc
        args.subject = config['subject'] if 'subject' in config else args.subject
        args.message = config['message'] if 'message' in config else args.message
        args.file = config['file'] if 'file' in config else args.file
        args.credentials = config['credentials'] if 'credentials' in config else args.credentials
        args.token = config['token'] if 'token' in config else args.token
        args.attach = config['attach'] if 'attach' in config else args.attach

if not args.to or not args.sender or not args.subject or not args.message:
    parser.print_help()
    sys.exit(1)

if __name__ == '__main__':
    main(args)
